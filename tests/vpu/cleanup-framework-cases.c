/* SPDX-License-Identifier: GPL-2.0-only */
/* FRAMEWORK_FIXTURE */

static struct iris_buffer work[4];
static struct v4l2_m2m_dev m2m_devices[3];
static struct file files[3];
static void clear_firmware(struct iris_inst *i)
{
    struct vb2_queue *queues[]={&i->m2m_ctx->sq,&i->m2m_ctx->dq};
    for(unsigned j=0;j<2;j++)for(unsigned k=0;k<queues[j]->max_num_buffers;k++)
        if(queues[j]->bufs[k])queues[j]->bufs[k]->firmware_owned=false;
}
static bool member(struct iris_inst *i)
{
    struct iris_inst *p;
    list_for_each_entry(p,&i->core->instances,list)if(p==i)return true;
    return false;
}
static int wait_for_completion_timeout(struct completion *completion,unsigned timeout)
{
    (void)timeout;
    if(wait_status)return 0;
    for(unsigned n=0;n<3;n++)if(completion==&inst[n].completion) {
        struct iris_hfi_packet ack={.flags=HFI_FW_FLAGS_SUCCESS};
        CHECK(!inst[n].lock.held);
        clear_firmware(&inst[n]);
        mutex_lock(&inst[n].lock);
        iris_hfi_gen2_handle_session_close(&inst[n],&ack);
        mutex_unlock(&inst[n].lock);
        return completion->done;
    }
    CHECK(false);return 0;
}
static int iris_queue_buffer(struct iris_inst *i,struct iris_buffer *b)
{
    CHECK(!i->core->resources.uncertain);
    dispatch_attempts++;
    if(dispatch_attempts==dispatch_fail_at)return -EIO;
    CHECK(!iris_sm8475_policy(i->core) || i->reservation.state==IRIS_RES_RESERVED);
    b->base.vb.vb2_buf.firmware_owned=true;
    b->attr=BUF_ATTR_QUEUED;dispatches++;return 0;
}
static void framework_buf_queue(struct vb2_buffer *b) { iris_vb2_buf_queue(b); }
static void kfree(void *p)
{
    for(unsigned i=0;i<3;i++) {
        if(p==&contexts[i])contexts_freed++;
        if(p==&inst[i])instances_freed++;
    }
}
static void fixture_queue(unsigned which,unsigned type,unsigned first,unsigned count)
{
    struct vb2_queue *q=v4l2_m2m_get_vq(&contexts[which],type);
    memset(q,0,sizeof(*q));q->inst=&inst[which];q->type=type;q->is_output=type==10;
    q->max_num_buffers=4;INIT_LIST_HEAD(&q->queued_list);INIT_LIST_HEAD(&q->done_list);
    INIT_LIST_HEAD(&contexts[which].out_q_ctx.rdy_queue);
    INIT_LIST_HEAD(&contexts[which].cap_q_ctx.rdy_queue);
    for(unsigned j=0;j<count;j++) {
        struct iris_buffer *b=&work[first+j];memset(b,0,sizeof(*b));
        b->base.vb.vb2_buf=(struct vb2_buffer){.vb2_queue=q,.type=type,.index=j,.state=VB2_BUF_STATE_QUEUED,
            .planes={{.length=100000,.bytesused=1000}}};
        INIT_LIST_HEAD(&b->base.vb.vb2_buf.queued_entry);
        INIT_LIST_HEAD(&b->base.vb.vb2_buf.done_entry);
        q->bufs[j]=&b->base.vb.vb2_buf;
        list_add_tail(&q->bufs[j]->queued_entry,&q->queued_list);q->queued_count++;
    }
}
static void fixture(void)
{
    reset();memset(work,0,sizeof(work));memset(m2m_devices,0,sizeof(m2m_devices));
    framework_warnings=memory_finishes=mappings_freed=contexts_freed=modules_held=devices_held=instances_freed=fh_exits=0;
    unsafe_completion=dispatch_attempts=dispatch_fail_at=close_calls=stop_calls=0;
    require_closed_cancel=false;
    for(unsigned i=0;i<3;i++) {
        contexts[i].m2m_dev=&m2m_devices[i];inst[i].m2m_dev=&m2m_devices[i];
        files[i]=(struct file){.inst=&inst[i],.fh={&contexts[i]}};
        inst[i].once_per_session_set=true;
        fixture_queue(i,10,0,0);fixture_queue(i,9,0,0);
    }
    add(0);inst[0].frame_rate=480;iris_sm8475_configure(&inst[0]);
    fixture_queue(0,10,0,2);
}
static void failed_start(void)
{
    fixture();dispatch_fail_at=2;wait_status=-EIO;
    CHECK(iris_policy_streamon(&files[0],NULL,10)==-EIO);
    CHECK(dispatches==1 && core.resources.uncertain && !inst[0].reservation.closed);
    CHECK(contexts[0].sq.owned_by_drv_count==2 && contexts[0].sq.streaming);
    CHECK(work[0].base.vb.vb2_buf.state==VB2_BUF_STATE_ACTIVE);
    CHECK(work[0].base.vb.vb2_buf.firmware_owned && !completed && !framework_warnings);
    int memory_before=memory_finishes;
    CHECK(iris_policy_streamoff(&files[0],NULL,10)==-EIO);
    CHECK(memory_finishes==memory_before && contexts[0].sq.owned_by_drv_count==2);
    struct v4l2_requestbuffers request={0};CHECK(iris_policy_reqbufs(&files[0],NULL,&request)==-EIO);
    CHECK(!mappings_freed && !reqbufs_calls && !unsafe_completion);
    CHECK(iris_policy_streamon(&files[0],NULL,10)==-EIO && dispatches==1);
    /* Actual successful CLOSE response, not a generic completion or timeout. */
    struct iris_hfi_packet ack={.flags=HFI_FW_FLAGS_SUCCESS};
    clear_firmware(&inst[0]);iris_hfi_gen2_handle_session_close(&inst[0],&ack);
    CHECK(inst[0].reservation.closed);
    CHECK(iris_policy_streamoff(&files[0],NULL,10)==0);
    CHECK(!contexts[0].sq.owned_by_drv_count && !contexts[0].sq.streaming);
    CHECK(work[0].base.vb.vb2_buf.done_calls==1 && work[1].base.vb.vb2_buf.done_calls==1);
    CHECK(!framework_warnings && !unsafe_completion && !mappings_freed);
}
static void nonstreaming_cancel(void)
{
    fixture();CHECK(admit(0)==0);
    contexts[0].sq.streaming=false;contexts[0].sq.start_streaming_called=false;
    work[0].base.vb.vb2_buf.firmware_owned=true;
    mutex_lock(&core.lock);iris_sm8475_fault(&core,-EIO);mutex_unlock(&core.lock);
    hfi_stop_error=-EIO;wait_status=-EIO;
    CHECK(iris_policy_streamoff(&files[0],NULL,10)==-EIO);
    CHECK(!memory_finishes && !mappings_freed && contexts[0].sq.queued_count==2);
    CHECK(work[0].base.vb.vb2_buf.firmware_owned && !unsafe_completion);
}
static void successful_close(void)
{
    fixture();inst[0].frame_rate=30;iris_sm8475_configure(&inst[0]);
    CHECK(admit(0)==0);add(1);CHECK(admit(1)==0);
    struct iris_reservation survivor=inst[1].reservation;
    fixture_queue(0,9,2,1);
    CHECK(iris_policy_streamon(&files[0],NULL,10)==0);
    CHECK(iris_policy_streamon(&files[0],NULL,9)==0);
    CHECK(dispatches==3 && inst[0].state==IRIS_INST_STREAMING);
    CHECK(iris_policy_streamon(&files[0],NULL,10)==0 && dispatches==3);
    require_closed_cancel=true;
    CHECK(iris_close(&files[0])==0);
    CHECK(close_calls==1 && !stop_calls && inst[0].reservation.closed);
    CHECK(instances_freed==1 && contexts_freed==1 && mappings_freed==3);
    CHECK(!framework_warnings && !unsafe_completion && !core.resources.uncertain);
    CHECK(device.pm_refs==1 && !modules_held && !devices_held);
    CHECK(!memcmp(&survivor,&inst[1].reservation,sizeof(survivor)));
    CHECK(core.resources.applied.ddr==survivor.demand.ddr && core.resources.applied.llcc==survivor.demand.llcc);
    for(unsigned j=0;j<3;j++)CHECK(work[j].base.vb.vb2_buf.done_calls==1);
}
static void quarantined_close(void)
{
    fixture();dispatch_fail_at=2;wait_status=-EIO;
    CHECK(iris_policy_streamon(&files[0],NULL,10)==-EIO);
    CHECK(iris_close(&files[0])==-ETIMEDOUT);
    CHECK(inst[0].reservation.quarantined && !inst[0].reservation.closed);
    CHECK(!mappings_freed && !contexts_freed && !instances_freed && !unsafe_completion);
    CHECK(modules_held==1 && devices_held==1 && device.pm_refs==2);
    struct {struct iris_hfi_header h;struct iris_hfi_packet p;} response={
        .h={.size=sizeof(response),.num_packets=1},
        .p={.size=sizeof(struct iris_hfi_packet),.type=HFI_CMD_CLOSE,.flags=HFI_FW_FLAGS_SUCCESS}};
    clear_firmware(&inst[0]);CHECK(iris_sm8475_quarantined_response(&inst[0],&response.h));
    CHECK(inst[0].reservation.closed && !mappings_freed && !completed);
    CHECK(modules_held==1 && devices_held==1 && device.pm_refs==2);
}
static void preflight_rejection(void)
{
    fixture();dimensions(0,1920,1088,480);
    CHECK(iris_policy_streamon(&files[0],NULL,10)==-ERANGE);
    CHECK(!dispatches && !unsafe_completion && !framework_warnings);
    CHECK(iris_policy_streamoff(&files[0],NULL,10)==0);
    CHECK(iris_close(&files[0])==0 && !modules_held && !devices_held && !device.pm_refs);
}
static void legacy_normal(void)
{
    fixture();platform.checked_vpu2_policy=false;
    CHECK(iris_policy_streamon(&files[0],NULL,10)==0);
    CHECK(dispatches==2 && contexts[0].sq.streaming && contexts[0].sq.owned_by_drv_count==2);
    CHECK(iris_policy_streamoff(&files[0],NULL,10)==0);
    CHECK(!contexts[0].sq.streaming && !contexts[0].sq.owned_by_drv_count && !unsafe_completion);
    CHECK(!device.pm_refs && !modules_held && !devices_held && !framework_warnings);
}
int main(int argc,char **argv)
{
    const char *name=argc>1?argv[1]:"all";
    if(!strcmp(name,"all")||!strcmp(name,"failed-start"))failed_start();
    if(!strcmp(name,"all")||!strcmp(name,"nonstreaming-cancel"))nonstreaming_cancel();
    if(!strcmp(name,"all")||!strcmp(name,"successful-close"))successful_close();
    if(!strcmp(name,"all")||!strcmp(name,"quarantined-close"))quarantined_close();
    if(!strcmp(name,"all")||!strcmp(name,"preflight-rejection"))preflight_rejection();
    if(!strcmp(name,"all")||!strcmp(name,"legacy-normal"))legacy_normal();
    printf("{\"status\":\"PASS\",\"case\":\"%s\",\"assertions\":%u}\n",name,checks);
    return 0;
}
