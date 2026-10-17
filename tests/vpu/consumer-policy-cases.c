/* SPDX-License-Identifier: GPL-2.0-only */
static struct iris_core core;
static struct device device;
static struct dev_pm_domain_list domains;
static struct iris_platform_data platform;
static struct platform_inst_caps caps;
static struct clk_bulk_data clks[2];
static const struct platform_clk_data clk_desc[]={{IRIS_HW_CLK,"vcodec0_core"},{IRIS_CTRL_CLK,"core"}};
static struct icc_bulk_data paths[3];
static struct icc_path iccs[3];
static struct iris_inst inst[3];
static struct v4l2_format src[3],dst[3];
static struct v4l2_m2m_ctx contexts[3];
static struct iris_buffer buffers[3];
static unsigned scenarios;
static int close_mock(struct iris_inst *i) { (void)i; return close_status; }
static int hfi_mock(struct iris_inst *i,u32 p) { (void)p;CHECK(!i->core->resources.uncertain);hfi_commands++;return 0; }
static int stop_mock(struct iris_inst *i,u32 p) { (void)i;(void)p;return hfi_stop_error; }
static const struct iris_hfi_session_ops session_ops={.session_close=close_mock,.session_start=hfi_mock,.session_stop=stop_mock,.session_pause=hfi_mock,.session_resume_drc=hfi_mock,.session_resume_drain=hfi_mock};
static u64 legacy_freq(struct iris_inst *i,size_t s) { (void)i; return 100000000+s; }
static struct vpu_ops ops={legacy_freq};
static const struct bw_info bw_table[]={{500000,5000},{0,1000}};
static void reset(void)
{
    memset(&core,0,sizeof(core));memset(inst,0,sizeof(inst));memset(contexts,0,sizeof(contexts));memset(buffers,0,sizeof(buffers));
    device=(struct device){.core=&core};domains.num_pds=2;
    caps=(struct platform_inst_caps){96,8192,96,8192,138240};
    platform=(struct iris_platform_data){.checked_vpu2_policy=true,.inst_caps=&caps,
        .max_session_count=16,.max_core_mbpf=276480,.max_core_mbps=7833600,
        .clk_tbl=clk_desc,.clk_tbl_size=2,.vpu_ops=&ops,.bw_tbl_dec=bw_table,.bw_tbl_dec_size=2};
    core.iris_platform_data=&platform;core.dev=&device;core.opp_pmdomain_tbl=&domains;
    source=(struct clk){720000000,NULL};hw_div=(struct clk){240000000,&source};ctrl_div=(struct clk){360000000,&source};
    hw_clk=(struct clk){240000000,&hw_div};ctrl_clk=(struct clk){360000000,&ctrl_div};
    clks[0]=(struct clk_bulk_data){"vcodec0_core",&hw_clk};clks[1]=(struct clk_bulk_data){"core",&ctrl_clk};
    core.clock_tbl=clks;core.clk_count=2;core.icc_tbl=paths;core.icc_count=3;
    const char *names[]={"cpu-cfg","video-mem","video-llcc"};
    for(int i=0;i<3;i++){iccs[i]=(struct icc_path){i,0};paths[i]=(struct icc_bulk_data){names[i],&iccs[i],0,0};}
    const unsigned long rates[]={240000000,338000000,366000000,444000000};
    const u32 levels[][2]={{128,64},{128,128},{192,192},{256,256}};
    for(int i=0;i<4;i++)opps[i]=(struct dev_pm_opp){rates[i],{levels[i][0],levels[i][1]},true};
    INIT_LIST_HEAD(&core.instances);
    for(int i=0;i<3;i++){
        src[i].fmt.pix_mp=(struct v4l2_pix_format_mplane){1280,720,V4L2_PIX_FMT_H264};
        dst[i].fmt.pix_mp=(struct v4l2_pix_format_mplane){1280,736,V4L2_PIX_FMT_NV12};
        inst[i].core=&core;inst[i].fmt_src=&src[i];inst[i].fmt_dst=&dst[i];inst[i].frame_rate=30;
        inst[i].codec=V4L2_PIX_FMT_H264;inst[i].domain=DECODER;inst[i].fw_caps[0].value=BIT_DEPTH_8;
        inst[i].m2m_ctx=&contexts[i];inst[i].session_id=(u32)i+1;inst[i].hfi_session_ops=&session_ops;
        contexts[i].sq=(struct vb2_queue){&inst[i],10,true,false};contexts[i].dq=(struct vb2_queue){&inst[i],9,true,false};
        buffers[i].base.vb.vb2_buf=(struct vb2_buffer){.vb2_queue=&contexts[i].sq,.type=10,.planes={{.length=100000,.bytesused=1000}}};
        buffers[i].type=BUF_INPUT;
    }
    op_number=provider_calls=fail_op=fail_second=dispatches=completed=0;
    close_status=wait_status=gets=pm_puts=pm_fail=readback_mode=0;
    hfi_commands=hfi_stop_error=opp_cached_mode=streamoff_cancelled=reqbufs_calls=0;opp_current=NULL;round_override=LONG_MIN;fake_time=0;memset(log_ops,0,sizeof(log_ops));
    scenarios++;
}
static void add(int i)
{
    list_add_tail(&inst[i].list,&core.instances);
    iris_sm8475_configure(&inst[i]);
}
static int admit(int i)
{
    mutex_lock(&inst[i].lock);int ret=iris_sm8475_admit(&inst[i]);mutex_unlock(&inst[i].lock);return ret;
}
static int apply(struct iris_resource_vector *v)
{
    mutex_lock(&core.lock);int ret=iris_sm8475_apply(&core,v);mutex_unlock(&core.lock);return ret;
}
static void dimensions(int i,u32 w,u32 h,u32 fps)
{
    src[i].fmt.pix_mp.width=w;src[i].fmt.pix_mp.height=h;
    dst[i].fmt.pix_mp.width=DIV_ROUND_UP(w,128)*128;dst[i].fmt.pix_mp.height=DIV_ROUND_UP(h,32)*32;
    inst[i].frame_rate=fps;iris_sm8475_configure(&inst[i]);
}
static void adapter_cases(void)
{
    struct iris_reservation r;
    reset();add(0);
    CHECK(iris_sm8475_adapt(&inst[0],0,&r)==0);
    CHECK(r.demand.ddr && r.demand.llcc && r.demand.freq==22680000);
    for(int c=0;c<3;c++)for(int f=0;f<2;f++){
        inst[0].codec=(u32[]){V4L2_PIX_FMT_H264,V4L2_PIX_FMT_HEVC,V4L2_PIX_FMT_VP9}[c];
        dimensions(0,1280,704,30);dst[0].fmt.pix_mp.pixelformat=f?V4L2_PIX_FMT_P010:V4L2_PIX_FMT_NV12;
        inst[0].fw_caps[0].value=f?BIT_DEPTH_10:BIT_DEPTH_8;
        CHECK(iris_sm8475_adapt(&inst[0],1000,&r)==(c==0&&f?-EINVAL:0));
        if(!(c==0&&f))CHECK(r.input.codec==(enum iris_vpu2_bw_codec)c);
    }
    inst[0].fw_caps[0].value=BIT_DEPTH_8;CHECK(iris_sm8475_adapt(&inst[0],0,&r)==-EINVAL);
    dst[0].fmt.pix_mp.pixelformat=V4L2_PIX_FMT_QC08C;CHECK(iris_sm8475_adapt(&inst[0],0,&r)==-EINVAL);
    dst[0].fmt.pix_mp.pixelformat=V4L2_PIX_FMT_NV12;inst[0].domain=ENCODER;CHECK(iris_sm8475_adapt(&inst[0],0,&r)==-EINVAL);
    reset();add(0);dimensions(0,96,8192,409);
    CHECK(iris_sm8475_adapt(&inst[0],1000,&r)==0 && r.demand.ddr==47271000);
    CHECK(admit(0)==-ERANGE && !provider_calls && !dispatches && !device.pm_refs);
    dimensions(0,96,8192,410);CHECK(admit(0)==-ERANGE && !provider_calls && !device.pm_refs);
    dimensions(0,1920,1088,480);CHECK(iris_sm8475_adapt(&inst[0],0,&r)==0 && r.demand.freq==822528000);
    CHECK(admit(0)==-ERANGE && !provider_calls); /* 1080p startup: strict clock ceiling */
    dimensions(0,3840,2160,480);CHECK(admit(0)==-ENOMEM && !provider_calls);
    dimensions(0,1280,720,480);CHECK(admit(0)==0 && inst[0].reservation.pm_held);
    CHECK(core.resources.applied.opp==366000000 && device.pm_refs==1);
    reset();add(0);inst[0].operating_rate=480;CHECK(admit(0)==0);
    CHECK(inst[0].reservation.demand.freq==362880000);
    reset();add(0);inst[0].operating_rate=481;CHECK(admit(0)==-EINVAL && !provider_calls);
    u64 freq=123;CHECK(iris_sm8475_frequency(1280,720,480,UINT64_MAX,&freq)==-ERANGE && !freq);
    struct iris_buffer b={0};b.base.vb.vb2_buf=buffers[0].base.vb.vb2_buf;
    b.base.vb.vb2_buf.planes[0].data_offset=1001;
    CHECK(iris_vb2_buffer_to_driver(&b.base.vb.vb2_buf,&b)==-EINVAL);
    b.base.vb.vb2_buf.planes[0].data_offset=0;b.base.vb.vb2_buf.planes[0].bytesused=100001;
    CHECK(iris_vb2_buffer_to_driver(&b.base.vb.vb2_buf,&b)==-EINVAL);
}
static void admission_cases(void)
{
    struct iris_resource_vector total;
    struct iris_reservation proposal={.state=IRIS_RES_RESERVED,.demand={.ddr=15000000,.llcc=15000000,.freq=1000}};
    reset();add(0);mutex_lock(&core.lock);
    CHECK(iris_sm8475_aggregate(&inst[0],&proposal,&total)==0);
    proposal.demand.llcc++;CHECK(iris_sm8475_aggregate(&inst[0],&proposal,&total)==-ERANGE);
    proposal.demand.llcc--;proposal.demand.ddr++;CHECK(iris_sm8475_aggregate(&inst[0],&proposal,&total)==-ERANGE);
    mutex_unlock(&core.lock);
    reset();add(0);add(1);CHECK(admit(0)==0);CHECK(admit(1)==0);
    u64 d=inst[0].reservation.demand.ddr,l=inst[0].reservation.demand.llcc;
    CHECK(core.resources.applied.ddr==2*d && core.resources.applied.llcc==2*l);
    inst[0].reservation.demand.llcc+=123;
    CHECK(admit(1)==0 && core.resources.applied.llcc==2*l+123);
    struct iris_reservation old=inst[0].reservation;
    contexts[0].src[0]=&buffers[0];contexts[0].ns=1;buffers[0].data_size=UINT32_MAX;
    CHECK(admit(0)==-ERANGE);
    CHECK(!memcmp(&old,&inst[0].reservation,sizeof(old)) && device.pm_refs==2);
    contexts[0].ns=0; /* outstanding demand survives an empty ready queue */
    CHECK(admit(0)==0 && inst[0].reservation.demand.llcc==old.demand.llcc);
    mutex_lock(&inst[0].lock);inst[0].reservation.closed=true;
    CHECK(iris_sm8475_release(&inst[0])==0);mutex_unlock(&inst[0].lock);
    CHECK(core.resources.applied.ddr==d && core.resources.applied.llcc==l && device.pm_refs==1);
    mutex_lock(&core.lock);CHECK(iris_sm8475_suspend(&core)==-EBUSY);mutex_unlock(&core.lock);
    reset();add(0);add(1);platform.max_session_count=1;CHECK(admit(0)==-ENOMEM);
    platform.max_session_count=16;inst[1].admission_mbpf=276480;CHECK(admit(0)==-ENOMEM);
    inst[1].admission_mbpf=1;inst[1].admission_mbps=7833600;CHECK(admit(0)==-ENOMEM);
    inst[1].admission_mbps=UINT64_MAX;CHECK(admit(0)==-ERANGE);
    reset();add(0);add(1);inst[1].reservation.state=IRIS_RES_RESERVED;
    inst[1].reservation.demand.ddr=UINT64_MAX;CHECK(admit(0)==-ERANGE);
    inst[1].reservation.demand.ddr=0;inst[1].reservation.demand.llcc=UINT64_MAX;CHECK(admit(0)==-ERANGE);
    inst[1].reservation.demand.llcc=0;inst[1].reservation.demand.freq=UINT64_MAX;CHECK(admit(0)==-ERANGE);
}
static void opp_cases(void)
{
    struct iris_resource_vector v;
    const u64 demands[]={1,240000000,240000001,338000001,366000001,444000000};
    const unsigned long selected[]={240000000,240000000,338000000,366000000,444000000,444000000};
    reset();for(int j=0;j<6;j++){v=(struct iris_resource_vector){.freq=demands[j]};CHECK(iris_sm8475_select_opp(&core,&v)==0 && v.opp==selected[j]);}
    v=(struct iris_resource_vector){.freq=444000001};CHECK(iris_sm8475_select_opp(&core,&v)==-ERANGE);
    v.freq=1;opps[0].levels[0]=64;CHECK(iris_sm8475_select_opp(&core,&v)==-EINVAL);opps[0].levels[0]=128;
    round_override=-EIO;CHECK(iris_sm8475_select_opp(&core,&v)==-EIO);
    round_override=239999999;v.freq=240000000;CHECK(iris_sm8475_select_opp(&core,&v)==-ERANGE);
    round_override=338000000;v=(struct iris_resource_vector){.freq=240000000};CHECK(iris_sm8475_select_opp(&core,&v)==0 && v.opp==338000000);
    round_override=444000001;v.opp=0;CHECK(iris_sm8475_select_opp(&core,&v)==-ERANGE);
    round_override=0;CHECK(iris_sm8475_select_opp(&core,&v)==-ERANGE);
    reset();CHECK(iris_sm8475_icc(&core,"video-mem",(u64)UINT32_MAX+1)==-ERANGE && !provider_calls);
    reset();add(0);core.icc_tbl[1].path=NULL;CHECK(admit(0)==-ENODEV && core.resources.uncertain && device.pm_refs==1);
    reset();domains.num_pds=1;v=(struct iris_resource_vector){.freq=1};CHECK(iris_sm8475_select_opp(&core,&v)==-ENODEV);
    reset();for(int j=0;j<4;j++)opps[j].available=false;CHECK(iris_sm8475_select_opp(&core,&v)==-ERANGE);
    reset();v=(struct iris_resource_vector){.cnoc=1000,.ddr=1000,.llcc=2000,.freq=100};CHECK(apply(&v)==0);
    CHECK(v.actual==240000000 && core.resources.ctrl_div==2 && !memcmp(log_ops,"CDLOOLDC",8));
    reset();v=(struct iris_resource_vector){.cnoc=1000,.ddr=1000,.llcc=2000,.freq=100};
    readback_mode=2;CHECK(apply(&v)==-ERANGE && !core.resources.applied.opp);
    reset();readback_mode=1;CHECK(apply(&v)==-ERANGE);
    reset();readback_mode=3;CHECK(apply(&v)==-ERANGE);
}
static void failure_cases(void)
{
    for(int failed=1;failed<=8;failed++){
        reset();add(0);CHECK(admit(0)==0);
        struct iris_resource_vector old=core.resources.applied;
        struct iris_reservation reserved=inst[0].reservation;
        op_number=provider_calls=0;fail_op=failed;
        dimensions(0,1280,720,60);
        CHECK(admit(0)==-EIO);
        CHECK(!memcmp(&core.resources.applied,&old,sizeof(old)));
        if(failed==4 || failed==5) {
            CHECK(core.resources.uncertain && core.resources.opp_uncertain && device.pm_refs==2);
            CHECK(inst[0].reservation.demand.ddr==reserved.demand.ddr);
            CHECK(core.resources.rollback_error==-EIO);
        } else {
            CHECK(!memcmp(&inst[0].reservation,&reserved,sizeof(reserved)));
            CHECK(!core.resources.uncertain && device.pm_refs==1);
            CHECK(!core.resources.rollback_error);
        }
        CHECK(!dispatches);
        CHECK(iccs[1].bw==old.ddr && iccs[2].bw==old.llcc && hw_clk.rate==old.actual);
        CHECK(core.resources.error==-EIO);
    }
    /* Every rollback position can fail, including the originally failed path. */
    for(int repair=1;repair<=7;repair++){
        reset();add(0);CHECK(admit(0)==0);
        struct iris_resource_vector old=core.resources.applied;
        op_number=provider_calls=0;fail_op=2;fail_second=2+repair;
        CHECK(admit(0)==-EIO);
        CHECK(core.resources.uncertain && core.resources.rollback_error==-EIO);
        CHECK(!memcmp(&core.resources.applied,&old,sizeof(old)));
        CHECK(device.pm_refs==2 && contexts[0].sq.error && contexts[0].dq.error);
        CHECK(admit(0)==-EIO && device.pm_refs==2);
        mutex_lock(&core.lock);CHECK(iris_sm8475_suspend(&core)==-EIO);mutex_unlock(&core.lock);
    }
    for(int failed=1;failed<=4;failed++){
        reset();add(0);CHECK(admit(0)==0);
        struct iris_resource_vector old=core.resources.applied;
        op_number=provider_calls=0;fail_op=failed;
        mutex_lock(&core.lock);CHECK(iris_sm8475_unvote(&core)==-EIO);mutex_unlock(&core.lock);
        CHECK(provider_calls==4 && !memcmp(log_ops,"OLDC",4));
        CHECK(core.resources.uncertain && !memcmp(&old,&core.resources.applied,sizeof(old)));
    }
    reset();add(0);CHECK(admit(0)==0);
    struct iris_resource_vector cached=core.resources.applied;
    opp_cached_mode=1;opp_current=&opps[0];op_number=provider_calls=0;fail_op=4;
    dimensions(0,1280,720,480);CHECK(admit(0)==-EIO);
    CHECK(core.resources.opp_uncertain && core.resources.uncertain && hw_clk.rate==cached.actual);
    CHECK(!memcmp(&cached,&core.resources.applied,sizeof(cached)));
    inst[0].reservation.closed=true;fail_op=0;
    CHECK(iris_sm8475_recover_idle(&core)==-EIO && device.pm_refs==2);
    reset();add(0);pm_fail=-EIO;CHECK(admit(0)==-EIO && !device.pm_refs && !provider_calls);
    reset();add(0);CHECK(admit(0)==0);mutex_lock(&inst[0].lock);
    inst[0].once_per_session_set=true;wait_status=-EIO;
    CHECK(iris_sm8475_close_session(&inst[0])==-EIO && !inst[0].reservation.closed);
    CHECK(iris_sm8475_release(&inst[0])==-EIO && device.pm_refs==2);
    mutex_unlock(&inst[0].lock);
    CHECK(iris_sm8475_recover_idle(&core)==-EBUSY && device.pm_refs==2);
    inst[0].reservation.closed=true;op_number=0;fail_op=2;
    CHECK(iris_sm8475_recover_idle(&core)==-EIO && device.pm_refs==2);
    fail_op=0;CHECK(iris_sm8475_recover_idle(&core)==0);
    CHECK(!device.pm_refs && !core.resources.uncertain && !core.resources.applied.cnoc);
    CHECK(inst[0].reservation.state==IRIS_RES_INACTIVE);
    reset();add(0);CHECK(admit(0)==0);mutex_lock(&inst[0].lock);
    CHECK(iris_sm8475_close_session(&inst[0])==0 && iris_sm8475_release(&inst[0])==0);
    mutex_unlock(&inst[0].lock);CHECK(!device.pm_refs && core.resources.applied.cnoc==1000);
    mutex_lock(&core.lock);CHECK(iris_sm8475_suspend(&core)==0 && iris_sm8475_unvote(&core)==0);mutex_unlock(&core.lock);
    CHECK(!core.resources.applied.ddr && !core.resources.applied.llcc && !core.resources.applied.cnoc);
}
static void dispatch_cases(void)
{
    reset();add(0);dimensions(0,1920,1088,480);
    iris_vb2_buf_queue(&buffers[0].base.vb.vb2_buf);
    CHECK(!dispatches && completed==1 && !contexts[0].ns && contexts[0].sq.error);
    CHECK(buffers[0].attr & BUF_ATTR_BUFFER_DONE);
    reset();add(0);contexts[0].sq.streaming=false;
    iris_vb2_buf_queue(&buffers[0].base.vb.vb2_buf);
    CHECK(!dispatches && !completed && buffers[0].attr==BUF_ATTR_DEFERRED);
    contexts[0].sq.streaming=true;mutex_lock(&inst[0].lock);
    CHECK(iris_queue_deferred_buffers(&inst[0],BUF_INPUT)==0);mutex_unlock(&inst[0].lock);
    CHECK(dispatches==1 && buffers[0].attr==BUF_ATTR_QUEUED && device.pm_refs==1);
    fake_time=NSEC_PER_SEC+1;
    reset();add(0);dimensions(0,1280,720,480);
    iris_vb2_buf_queue(&buffers[0].base.vb.vb2_buf);
    CHECK(dispatches==1 && inst[0].frame_rate==480);
    /* Fresh incoming buffer participates in the byte maximum before dispatch. */
    reset();add(0);buffers[0].base.vb.vb2_buf.planes[0].bytesused=100000;
    iris_vb2_buf_queue(&buffers[0].base.vb.vb2_buf);
    CHECK(dispatches==1 && inst[0].reservation.input.queued_bytes==100000);
    reset();add(0);buffers[0].base.vb.vb2_buf.planes[0].bytesused=1;buffers[0].base.vb.vb2_buf.planes[0].data_offset=1;
    iris_vb2_buf_queue(&buffers[0].base.vb.vb2_buf);CHECK(dispatches==1 && inst[0].reservation.demand.ddr);
    struct { struct iris_hfi_header h;struct iris_hfi_packet p; } cmd={.h={.size=sizeof(cmd),.session_id=1,.num_packets=1},.p={.size=sizeof(struct iris_hfi_packet),.type=HFI_CMD_BUFFER}};
    CHECK(iris_sm8475_hfi_allowed(&core,&cmd,sizeof(cmd))==0);
    mutex_lock(&core.lock);iris_sm8475_fault(&core,-EIO);mutex_unlock(&core.lock);
    CHECK(iris_sm8475_hfi_allowed(&core,&cmd,sizeof(cmd))==-EIO);
    cmd.p.type=HFI_CMD_CLOSE;CHECK(iris_sm8475_hfi_allowed(&core,&cmd,sizeof(cmd))==0);
    cmd.p.type=HFI_CMD_STOP;CHECK(iris_sm8475_hfi_allowed(&core,&cmd,sizeof(cmd))==0);
    cmd.p.type=HFI_CMD_START;CHECK(iris_sm8475_hfi_allowed(&core,&cmd,sizeof(cmd))==-EIO);
    inst[0].reservation.quarantined=true;cmd.p.type=HFI_CMD_BUFFER;
    CHECK(iris_sm8475_quarantined_response(&inst[0],&cmd.h) && !inst[0].reservation.closed);
    cmd.p.type=HFI_CMD_CLOSE;cmd.p.flags=HFI_FW_FLAGS_SUCCESS;
    CHECK(iris_sm8475_quarantined_response(&inst[0],&cmd.h) && inst[0].reservation.closed);
}
static void streaming_cases(void)
{
    reset();add(0);dimensions(0,1920,1088,480);
    mutex_lock(&inst[0].lock);CHECK(iris_process_streamon_input(&inst[0])==-ERANGE);mutex_unlock(&inst[0].lock);
    CHECK(!hfi_commands && !dispatches);
    reset();add(0);mutex_lock(&inst[0].lock);
    CHECK(iris_process_streamon_input(&inst[0])==0 && hfi_commands==1);
    /* Capture/DRC validates changed dimensions before resume or start. */
    inst[0].sub_state=IRIS_INST_SUB_DRC|IRIS_INST_SUB_DRC_LAST|IRIS_INST_SUB_INPUT_PAUSE;
    inst[0].state=IRIS_INST_INPUT_STREAMING;dimensions(0,1920,1088,480);
    CHECK(iris_process_streamon_output(&inst[0])==-ERANGE && hfi_commands==1);
    dimensions(0,1280,720,30);
    CHECK(iris_process_streamon_output(&inst[0])==0 && hfi_commands==3);
    struct iris_reservation saved=inst[0].reservation;
    CHECK(iris_session_streamoff(&inst[0],9)==0);
    CHECK(!memcmp(&saved,&inst[0].reservation,sizeof(saved)) && device.pm_refs==1);
    /* Capture stop and drain leave the committed reservation intact. */
    CHECK(iris_session_streamoff(&inst[0],10)==0 && device.pm_refs==1);
    mutex_unlock(&inst[0].lock);
    reset();add(0);CHECK(admit(0)==0);hfi_stop_error=-EIO;inst[0].once_per_session_set=true;
    wait_status=-EIO;mutex_lock(&inst[0].lock);
    CHECK(iris_session_streamoff(&inst[0],10)==-EIO && !inst[0].reservation.closed);
    CHECK(core.resources.uncertain && device.pm_refs==2);mutex_unlock(&inst[0].lock);
    reset();add(0);CHECK(admit(0)==0);hfi_stop_error=-EIO;inst[0].once_per_session_set=true;
    wait_status=-EIO;struct file file={&inst[0]};
    CHECK(iris_policy_streamoff(&file,NULL,10)==-EIO && !streamoff_cancelled && !completed);
    struct v4l2_requestbuffers request={0};CHECK(iris_policy_reqbufs(&file,NULL,&request)==-EIO && !reqbufs_calls);
    reset();add(0);CHECK(admit(0)==0);file.inst=&inst[0];
    CHECK(iris_policy_streamoff(&file,NULL,10)==0 && streamoff_cancelled==1 && inst[0].stopped_queues==BIT(10));
    /* Sampling reduces the proposal but cannot erase old in-flight demand. */
    reset();add(0);dimensions(0,1280,720,480);
    iris_vb2_buf_queue(&buffers[0].base.vb.vb2_buf);
    u64 high=inst[0].reservation.demand.freq;
    struct iris_buffer next=buffers[0];next.base.vb.vb2_buf.index=1;
    fake_time=2*NSEC_PER_SEC;iris_vb2_buf_queue(&next.base.vb.vb2_buf);
    CHECK(inst[0].frame_rate==30 && inst[0].reservation.input.frame_rate==30);
    CHECK(inst[0].reservation.demand.freq==high && dispatches==2 && device.pm_refs==1);
}
static void legacy_cases(void)
{
    reset();add(0);platform.checked_vpu2_policy=false;
    mutex_lock(&inst[0].lock);CHECK(iris_scale_power(&inst[0])==0);mutex_unlock(&inst[0].lock);
    CHECK(!provider_calls && !core.power.clk_freq && core.power.icc_bw==0);
    contexts[0].src[0]=&buffers[0];contexts[0].ns=1;buffers[0].data_size=1000;
    mutex_lock(&inst[0].lock);CHECK(iris_scale_power(&inst[0])==0);mutex_unlock(&inst[0].lock);
    CHECK(core.power.clk_freq==100001000 && inst[0].icc_data.fps==30 && core.power.icc_bw==5000);
    CHECK(!inst[0].reservation.pm_held && !device.pm_refs);
}
int main(void)
{
    adapter_cases();admission_cases();opp_cases();failure_cases();dispatch_cases();streaming_cases();legacy_cases();
    printf("{\"status\":\"PASS\",\"assertions\":%u,\"scenarios\":%u,\"provider_failure_positions\":8,\"rollback_failure_positions\":7,\"unvote_failure_positions\":4}\n",checks,scenarios);
    return 0;
}
