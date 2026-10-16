/* SPDX-License-Identifier: GPL-2.0-only */
/* External boundaries for unchanged VB2/M2M and Iris cleanup control flow. */
#define VB2_BUF_STATE_QUEUED_HOST VB2_BUF_STATE_QUEUED
#define __maybe_unused
enum media_request_state { MEDIA_REQUEST_STATE_QUEUED = 1 };
#define TRANS_QUEUED BIT(0)
#define THIS_MODULE ((void *)1)
static int framework_warnings, memory_finishes, mappings_freed, contexts_freed;
static int modules_held, devices_held, instances_freed, fh_exits;
static int unsafe_completion, dispatch_attempts, dispatch_fail_at, close_calls, stop_calls;
static bool require_closed_cancel;
#define atomic_read(p) (*(p))
#define atomic_set(p,v) (*(p)=(v))
#define atomic_inc(p) (++*(p))
#define atomic_dec(p) (--*(p))
#define WARN_ON(c) ({ bool _warn=!!(c); if(_warn) framework_warnings++;_warn; })
#define dprintk(...) ((void)0)
#define pr_warn(...) ((void)0)
#define trace_vb2_buf_done(...) ((void)0)
#define trace_vb2_buf_queue(...) ((void)0)
#define spin_lock_irqsave(l,f) do { (void)(l); (f)=0; } while(0)
#define spin_unlock_irqrestore(l,f) do { (void)(l); (void)(f); } while(0)
#define wake_up(...) ((void)0)
#define wake_up_all(...) ((void)0)
#define call_qop(q,op,...) framework_##op(__VA_ARGS__)
#define call_void_qop(q,op,...) framework_##op(__VA_ARGS__)
#define call_void_vb_qop(v,op,...) framework_##op(__VA_ARGS__)
#define call_void_bufop(q,op,...) ((void)(q),framework_##op(__VA_ARGS__))
static bool list_empty(const struct list_head *l) { return l->next==l; }
static void list_del(struct list_head *p) { p->next->prev=p->prev;p->prev->next=p->next; }
static void list_del_init(struct list_head *p) { list_del(p);INIT_LIST_HEAD(p); }
#define list_for_each_entry_safe(p,n,h,m) for(p=container_of((h)->next,__typeof__(*p),m),n=container_of(p->m.next,__typeof__(*p),m);&p->m!=(h);p=n,n=container_of(n->m.next,__typeof__(*n),m))
static struct vb2_buffer *vb2_get_buffer(struct vb2_queue *q,unsigned i) { return q->bufs[i]; }
static unsigned vb2_get_num_buffers(struct vb2_queue *q) { unsigned n=0;for(unsigned i=0;i<q->max_num_buffers;i++)n+=!!q->bufs[i];return n; }
static bool vb2_fileio_is_active(struct vb2_queue *q) { (void)q;return false; }
static bool vb2_start_streaming_called(struct vb2_queue *q) { return q->start_streaming_called; }
static void __vb2_buf_mem_finish(struct vb2_buffer *b) { if(b->firmware_owned)unsafe_completion++;memory_finishes++; }
static void framework_init_buffer(struct vb2_buffer *b) { (void)b; }
static void framework_buf_finish(struct vb2_buffer *b) { (void)b; }
static void framework_buf_request_complete(struct vb2_buffer *b) { (void)b;CHECK(false); }
static void media_request_object_unbind(struct request_object *r) { (void)r;CHECK(false); }
static void media_request_object_put(struct request_object *r) { (void)r;CHECK(false); }
static void media_request_put(struct media_request *r) { (void)r;CHECK(false); }
static int framework_prepare_streaming(struct vb2_queue *q) { (void)q;return 0; }
static void framework_unprepare_streaming(struct vb2_queue *q) { (void)q; }
int iris_vb2_start_streaming(struct vb2_queue *q,unsigned count);
void iris_vb2_stop_streaming(struct vb2_queue *q);
static int framework_start_streaming(struct vb2_queue *q,unsigned count) { return iris_vb2_start_streaming(q,count); }
static void framework_stop_streaming(struct vb2_queue *q) { iris_vb2_stop_streaming(q); }
static void framework_buf_queue(struct vb2_buffer *b);
void vb2_buffer_done(struct vb2_buffer *b,enum vb2_buffer_state s);
static void __vb2_queue_cancel(struct vb2_queue *q);
int v4l2_m2m_ioctl_streamon(struct file *f,void *h,enum v4l2_buf_type t);
void v4l2_m2m_ctx_release(struct v4l2_m2m_ctx *ctx);
void vb2_queue_release(struct vb2_queue *q);
static void v4l2_m2m_buf_done(struct vb2_v4l2_buffer *b,int state) {
    if(b->vb2_buf.firmware_owned)unsafe_completion++;
    b->vb2_buf.done_calls++;completed++;
    vb2_buffer_done(&b->vb2_buf,state);
}
int iris_vb2_buffer_done(struct iris_inst *i,struct iris_buffer *b);
void iris_helper_buffers_done(struct iris_inst *i,u32 type,enum vb2_buffer_state s);
static struct vb2_v4l2_buffer *v4l2_m2m_src_buf_remove(struct v4l2_m2m_ctx *m) {
 if(!m->ns){return NULL;}
 struct vb2_v4l2_buffer *b=&m->src[0]->base.vb;v4l2_m2m_src_buf_remove_by_buf(m,b);return b;
}
static struct vb2_v4l2_buffer *v4l2_m2m_dst_buf_remove(struct v4l2_m2m_ctx *m) {
 if(!m->nd){return NULL;}
 struct vb2_v4l2_buffer *b=&m->dst[0]->base.vb;v4l2_m2m_dst_buf_remove_by_buf(m,b);return b;
}
static struct vb2_v4l2_buffer *remove_index(struct v4l2_m2m_ctx *m,u32 type,u32 index) {
 struct iris_buffer **array=type==10?m->src:m->dst;int n=type==10?m->ns:m->nd;
 for(int k=0;k<n;k++)if(array[k]->index==index){struct vb2_v4l2_buffer *b=&array[k]->base.vb;
 if(type==10)v4l2_m2m_src_buf_remove_by_buf(m,b);else v4l2_m2m_dst_buf_remove_by_buf(m,b);return b;}return NULL;
}
static struct vb2_v4l2_buffer *v4l2_m2m_src_buf_remove_by_idx(struct v4l2_m2m_ctx *m,u32 index){return remove_index(m,10,index);}
static struct vb2_v4l2_buffer *v4l2_m2m_dst_buf_remove_by_idx(struct v4l2_m2m_ctx *m,u32 index){return remove_index(m,9,index);}
static void iris_get_ts_metadata(struct iris_inst *i,u64 ts,struct vb2_v4l2_buffer *b){(void)i;(void)ts;(void)b;}
#define V4L2_BUF_FLAG_ERROR BIT(6)
static int iris_check_session_supported(struct iris_inst *i) { (void)i;return 0; }
int iris_vdec_streamon_input(struct iris_inst *i);
int iris_vdec_streamon_output(struct iris_inst *i);
static int iris_venc_streamon_input(struct iris_inst *i) { (void)i;return 0; }
static int iris_venc_streamon_output(struct iris_inst *i) { (void)i;return 0; }
static int iris_queue_internal_deferred_buffers(struct iris_inst *i,enum iris_buffer_type t) { (void)i;(void)t;return 0; }
static int iris_set_properties(struct iris_inst *i,u32 t) { (void)i;(void)t;return 0; }
static int iris_alloc_and_queue_persist_bufs(struct iris_inst *i,u32 t) { (void)i;(void)t;return 0; }
static void iris_get_internal_buffers(struct iris_inst *i,u32 t) { (void)i;(void)t; }
static int iris_destroy_dequeued_internal_buffers(struct iris_inst *i,u32 t) { (void)i;(void)t;return 0; }
static int iris_create_internal_buffers(struct iris_inst *i,u32 t) { (void)i;(void)t;return 0; }
static int iris_queue_internal_buffers(struct iris_inst *i,u32 t) { (void)i;(void)t;return 0; }
#define BUF_PERSIST 3
static int iris_inst_state_change_streamon(struct iris_inst *i,u32 p) {
    i->state=(p==10?(i->state==IRIS_INST_OUTPUT_STREAMING?IRIS_INST_STREAMING:IRIS_INST_INPUT_STREAMING):
                       (i->state==IRIS_INST_INPUT_STREAMING?IRIS_INST_STREAMING:IRIS_INST_OUTPUT_STREAMING));return 0;
}
static struct v4l2_fh *file_to_v4l2_fh(struct file *f) { return &f->fh; }
static void v4l2_m2m_try_schedule(struct v4l2_m2m_ctx *m) { (void)m; }
static void v4l2_m2m_cancel_job(struct v4l2_m2m_ctx *m) { (void)m; }
static struct v4l2_m2m_queue_ctx *get_queue_ctx(struct v4l2_m2m_ctx *m,enum v4l2_buf_type t) { return t==10?&m->out_q_ctx:&m->cap_q_ctx; }
static void __vb2_cleanup_fileio(struct vb2_queue *q) { (void)q; }
static void __vb2_queue_free(struct vb2_queue *q,unsigned first,unsigned n) {
    for(unsigned i=first;i<first+n;i++)if(q->bufs[i]) {
        CHECK(!q->bufs[i]->firmware_owned);
        if(require_closed_cancel)CHECK(q->inst->reservation.closed);
        mappings_freed++;q->bufs[i]=NULL;
    }
}
static void vb2_core_free_buffers_storage(struct vb2_queue *q) { (void)q; }
static void v4l2_ctrl_handler_free(int *h) { (void)h; }
static void v4l2_m2m_release(struct v4l2_m2m_dev *d) { (void)d; }
static void iris_v4l2_fh_deinit(struct iris_inst *i,struct file *f) { (void)i;(void)f;fh_exits++; }
static void iris_destroy_all_internal_buffers(struct iris_inst *i,u32 t) { (void)t;CHECK(i->reservation.closed); }
static void iris_check_num_queued_internal_buffers(struct iris_inst *i,u32 t) { (void)i;(void)t; }
static void kfree(void *p);
static void __module_get(void *p) { (void)p;modules_held++; }
static struct device *get_device(struct device *d) { devices_held++;d->refs++;return d; }

static void complete(struct completion *c) { c->done=1; }

#define msecs_to_jiffies(ms) (ms)
#define HW_RESPONSE_TIMEOUT_VALUE 1000
static int wait_for_completion_timeout(struct completion *completion,unsigned timeout);
