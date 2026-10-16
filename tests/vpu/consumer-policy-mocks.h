/* SPDX-License-Identifier: GPL-2.0-only */
/* Host-only external API/type mocks. Production functions are extracted unchanged. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <errno.h>
#include <inttypes.h>
#include <linux/types.h>
typedef uint8_t u8;
#include <linux/overflow.h>
#define BIT(n) (1U << (n))
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define max(a,b) ({ __auto_type _a=(a); __auto_type _b=(b); _a>_b?_a:_b; })
#define max_t(t,a,b) max((t)(a),(t)(b))
#define clamp_t(t,x,a,b) max_t(t,a,((t)(x)>(t)(b)?(t)(b):(t)(x)))
#define DIV_ROUND_UP(a,b) (((a)+(b)-1)/(b))
#define U32_MAX UINT32_MAX
#define U64_MAX UINT64_MAX
#define ERR_PTR(x) ((void *)(intptr_t)(x))
#define PTR_ERR(p) ((int)(intptr_t)(p))
#define IS_ERR(p) ((uintptr_t)(p) >= (uintptr_t)-4095)
#define IS_ERR_OR_NULL(p) (!(p) || IS_ERR(p))
static u64 div64_u64(u64 a, u64 b) { return a/b; }
static u64 div_u64(u64 a, u32 b) { return a/b; }
static unsigned checks;
#define CHECK(x) do { checks++; if (!(x)) { fprintf(stderr,"check %u line %d: %s\n",checks,__LINE__,#x); exit(1); } } while(0)
struct mutex { bool held; };
static void mutex_lock(struct mutex *m) { CHECK(!m->held); m->held=true; }
static void mutex_unlock(struct mutex *m) { CHECK(m->held); m->held=false; }
#define lockdep_assert_held(m) CHECK((m)->held)
struct list_head { struct list_head *next, *prev; };
#define INIT_LIST_HEAD(p) ((p)->next=(p)->prev=(p))
static void list_add_tail(struct list_head *p,struct list_head *h) {
    p->next=h; p->prev=h->prev; h->prev->next=p; h->prev=p;
}
#define container_of(p,t,m) ((t *)((char *)(p)-offsetof(t,m)))
#define list_for_each_entry(p,h,m) for (p=container_of((h)->next,__typeof__(*p),m); &p->m!=(h); p=container_of(p->m.next,__typeof__(*p),m))
#include "iris_vpu2_bw.h"
/* PUBLIC_POWER_HEADER */
#define v4l2_fourcc(a,b,c,d) ((u32)(a)|((u32)(b)<<8)|((u32)(c)<<16)|((u32)(d)<<24))
/* SOURCE_CONSTANTS */
#define DEFAULT_FPS 30
#define MAXIMUM_FPS 480
#define BIT_DEPTH 0
#define DECODER 2
#define ENCODER 1
enum iris_buffer_type { BUF_INPUT, BUF_OUTPUT };
#define IRIS_INST_ERROR 9
enum iris_inst_sub_state {
 IRIS_INST_SUB_DRC=BIT(0), IRIS_INST_SUB_DRC_LAST=BIT(1), IRIS_INST_SUB_DRAIN=BIT(2),
 IRIS_INST_SUB_DRAIN_LAST=BIT(3), IRIS_INST_SUB_INPUT_PAUSE=BIT(4),
 IRIS_INST_SUB_OUTPUT_PAUSE=BIT(5), IRIS_INST_SUB_FIRST_IPSC=BIT(6)
};
#define IRIS_INST_INPUT_STREAMING 3
#define STAGE 1
#define PIPE 2
#define V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE 10
#define V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE 9
#define V4L2_TYPE_IS_OUTPUT(t) ((t)==10)
#define V4L2_TYPE_IS_CAPTURE(t) ((t)==9)
#define V4L2_FIELD_ANY 0
#define V4L2_FIELD_NONE 1
#define V4L2_EVENT_EOS 2
#define V4L2_BUF_FLAG_LAST BIT(0)
#define VB2_BUF_STATE_ERROR 5
#define VB2_BUF_STATE_DONE 4
#define NSEC_PER_SEC 1000000000ULL
enum platform_clk_type { IRIS_HW_CLK, IRIS_CTRL_CLK, IRIS_AXI_CLK };
struct iris_core;
struct device { struct iris_core *core; int pm_refs; };
struct clk { unsigned long rate; struct clk *parent; };
struct clk_bulk_data { const char *id; struct clk *clk; };
struct icc_path { int index; u32 bw; };
struct icc_bulk_data { const char *name; struct icc_path *path; u32 avg_bw, peak_bw; };
struct dev_pm_domain_list { u32 num_pds; };
struct dev_pm_opp { unsigned long hz; u32 levels[2]; bool available; };
struct platform_clk_data { int clk_type; const char *clk_name; };
struct platform_inst_caps { u32 min_frame_width, max_frame_width, min_frame_height, max_frame_height, max_mbpf; };
struct bw_info { u32 mbs_per_sec, bw_ddr; };
struct vpu_ops { u64 (*calc_freq)(struct iris_inst *,size_t); };
struct iris_platform_data {
    bool checked_vpu2_policy;
    struct platform_inst_caps *inst_caps;
    u32 max_session_count,max_core_mbpf,max_core_mbps;
    const struct platform_clk_data *clk_tbl;
    u32 clk_tbl_size;
    const struct bw_info *bw_tbl_dec;
    u32 bw_tbl_dec_size;
    struct vpu_ops *vpu_ops;
};
struct iris_core {
    struct mutex lock;
    struct list_head instances;
    struct iris_platform_data *iris_platform_data;
    struct iris_resource_state resources;
    struct device *dev;
    struct dev_pm_domain_list *opp_pmdomain_tbl;
    struct clk_bulk_data *clock_tbl;
    u32 clk_count,icc_count;
    struct icc_bulk_data *icc_tbl;
    struct { u64 clk_freq,icc_bw; } power;
};
struct v4l2_pix_format_mplane { u32 width,height,pixelformat; };
struct v4l2_format { struct { struct v4l2_pix_format_mplane pix_mp; } fmt; };
struct vb2_queue { struct iris_inst *inst; u32 type; bool streaming,error; };
struct vb2_buffer { struct vb2_queue *vb2_queue; u32 type,index; u64 timestamp;
    struct { u32 length,data_offset,bytesused; struct { int fd; } m; } planes[1]; };
struct vb2_v4l2_buffer { struct vb2_buffer vb2_buf; u32 flags,field,sequence; };
struct v4l2_m2m_buffer { struct vb2_v4l2_buffer vb; };
struct iris_buffer { struct v4l2_m2m_buffer base; u32 type,index,buffer_size,data_offset,data_size,flags,attr; int fd; u64 timestamp; };
struct v4l2_m2m_ctx { struct iris_buffer *src[16],*dst[16]; int ns,nd; struct vb2_queue sq,dq; bool stopped; };
struct icc_vote_data { u32 width,height,fps; };
struct iris_hfi_session_ops {
 int (*session_close)(struct iris_inst *);
 int (*session_start)(struct iris_inst *,u32);
 int (*session_stop)(struct iris_inst *,u32);
 int (*session_pause)(struct iris_inst *,u32);
 int (*session_resume_drc)(struct iris_inst *,u32);
 int (*session_resume_drain)(struct iris_inst *,u32);
};
struct iris_inst {
    struct list_head list;
    struct mutex lock;
    struct iris_core *core;
    struct v4l2_format *fmt_src,*fmt_dst;
    struct { u32 width,height; } crop;
    u32 frame_rate,operating_rate,domain,codec,session_id;
    struct { u32 value; } fw_caps[1];
    struct iris_reservation reservation;
    u64 admission_mbpf,admission_mbps;
    int admission_error;
    u32 stopped_queues;
    struct v4l2_m2m_ctx *m2m_ctx;
    struct { u64 min_freq,icc_bw; } power;
    size_t max_input_data_size;
    struct icc_vote_data icc_data;
    u64 last_buf_ns;
    u32 frame_counter,state,sub_state,sequence_cap;
    bool last_buffer_dequeued,once_per_session_set;
    int completion,fh;
    const struct iris_hfi_session_ops *hfi_session_ops;
};
#define to_iris_buffer(v) container_of(v,struct iris_buffer,base.vb)
#define to_vb2_v4l2_buffer(v) container_of(v,struct vb2_v4l2_buffer,vb2_buf)
#define v4l2_m2m_for_each_src_buf_safe(ctx,b,n) for(int _i=0;_i<(ctx)->ns && ((b)=&(ctx)->src[_i]->base,(n)=NULL,1);_i++)
static int op_number, fail_op, fail_second, provider_calls, dispatches, completed;
static int close_status, wait_status, gets, pm_puts, pm_fail;
static long round_override=LONG_MIN;
static int readback_mode, opp_cached_mode;
static struct dev_pm_opp *opp_current;
static struct dev_pm_opp opps[4];
static struct clk source,hw_div,ctrl_div,hw_clk,ctrl_clk;
static char log_ops[256];
static int event(char tag) {
    CHECK(provider_calls<(int)sizeof(log_ops));
    log_ops[provider_calls++]=tag;
    op_number++;
    return op_number==fail_op || op_number==fail_second ? -EIO : 0;
}
static struct clk *clk_get_parent(struct clk *c) { return c->parent; }
static bool clk_is_match(struct clk *a,struct clk *b) { return a==b; }
static unsigned long clk_get_rate(struct clk *c) { return c->rate; }
static long clk_round_rate(struct clk *c,unsigned long freq) { (void)c; return round_override==LONG_MIN?(long)freq:round_override; }
static struct dev_pm_opp *dev_pm_opp_find_freq_ceil(struct device *d,unsigned long *f) {
    (void)d;
    for(int i=0;i<4;i++) if(opps[i].available && opps[i].hz>=*f) { *f=opps[i].hz; return &opps[i]; }
    return ERR_PTR(-ERANGE);
}
static struct dev_pm_opp *dev_pm_opp_find_freq_exact(struct device *d,unsigned long f,bool avail) {
    (void)d; (void)avail;
    for(int i=0;i<4;i++) if(opps[i].available && opps[i].hz==f) return &opps[i];
    return ERR_PTR(-ERANGE);
}
static void dev_pm_opp_put(struct dev_pm_opp *p) { (void)p; }
static unsigned dev_pm_opp_get_required_pstate(struct dev_pm_opp *o,unsigned i) { return o->levels[i]; }
static int dev_pm_opp_set_opp(struct device *d,struct dev_pm_opp *o) {
    (void)d;
    if(opp_cached_mode && o && o==opp_current) return 0;
    int ret=event('O');
    if(opp_cached_mode && ret) return ret; /* required domain failed, clock unchanged */
    if(!ret) opp_current=o;
    /* Even failure can leave partial clock/domain changes. */
    unsigned long rate=o?o->hz:0;
    hw_clk.rate=hw_div.rate=rate;
    source.rate=rate*3;
    ctrl_clk.rate=ctrl_div.rate=source.rate/2;
    if(readback_mode==1) hw_clk.rate=0;
    if(readback_mode==2) ctrl_clk.rate++;
    if(readback_mode==3) source.rate++;
    return ret;
}
static int icc_set_bw(struct icc_path *p,u32 bw,u32 peak) {
    CHECK(!peak);
    char tags[]={'C','D','L'};
    int ret=event(tags[p->index]);
    p->bw=bw; /* failures may have hardware effects */
    return ret;
}
static int pm_runtime_resume_and_get(struct device *d) {
    CHECK(!d->core->lock.held);
    gets++;
    if(pm_fail) return pm_fail;
    d->pm_refs++; return 0;
}
static void pm_runtime_get_noresume(struct device *d) { d->pm_refs++; }
static void pm_runtime_put_autosuspend(struct device *d) { CHECK(!d->core->lock.held); CHECK(d->pm_refs>0); d->pm_refs--; pm_puts++; }
static bool pm_runtime_suspended(struct device *d) { (void)d; return false; }
static bool iris_split_mode_enabled(struct iris_inst *i) {
    u32 f=i->fmt_dst->fmt.pix_mp.pixelformat;
    return f==V4L2_PIX_FMT_NV12 || f==V4L2_PIX_FMT_P010 || f==V4L2_PIX_FMT_QC08C || f==V4L2_PIX_FMT_QC10C;
}
static void iris_vb2_queue_error(struct iris_inst *i) { i->m2m_ctx->sq.error=i->m2m_ctx->dq.error=true; }
static int iris_set_icc_bw(struct iris_core *c,unsigned long bw) { c->power.icc_bw=bw; return 0; }
static int iris_opp_set_rate(struct device *d,unsigned long freq) { d->core->power.clk_freq=freq; return 0; }
static struct vb2_queue *v4l2_m2m_get_vq(struct v4l2_m2m_ctx *m,u32 type) { return type==10?&m->sq:&m->dq; }
static bool vb2_is_streaming(struct vb2_queue *q) { return q->streaming; }
static void *vb2_get_drv_priv(struct vb2_queue *q) { return q->inst; }
static u64 fake_time;
static u64 ktime_get_ns(void) { return fake_time; }
static void iris_set_ts_metadata(struct iris_inst *i,struct vb2_v4l2_buffer *b) { (void)i; (void)b; }
static int iris_queue_buffer(struct iris_inst *i,struct iris_buffer *b) {
    CHECK(!i->core->resources.uncertain);
    CHECK(!iris_sm8475_policy(i->core) || i->reservation.state==IRIS_RES_RESERVED);
    dispatches++; b->attr=BUF_ATTR_QUEUED; return 0;
}
static int iris_venc_qbuf(struct iris_inst *i,struct vb2_v4l2_buffer *b) { return iris_queue_buffer(i,to_iris_buffer(b)); }
static int iris_inst_change_state(struct iris_inst *i,u32 s) { i->state=s; return 0; }
struct v4l2_event { u32 type; };
static void vb2_set_plane_payload(struct vb2_buffer *v,int p,u32 bytes) { v->planes[p].bytesused=bytes; }
static void v4l2_m2m_buf_done(struct vb2_v4l2_buffer *b,int state) { (void)b;(void)state;completed++; }
static bool v4l2_m2m_has_stopped(struct v4l2_m2m_ctx *m) { return m->stopped; }
static void v4l2_m2m_mark_stopped(struct v4l2_m2m_ctx *m) { m->stopped=true; }
static void v4l2_event_queue_fh(int *f,const struct v4l2_event *e) { (void)f; (void)e; }
static void v4l2_m2m_buf_queue(struct v4l2_m2m_ctx *m,struct vb2_v4l2_buffer *b) {
    if(b->vb2_buf.type==10) m->src[m->ns++]=to_iris_buffer(b);
    else m->dst[m->nd++]=to_iris_buffer(b);
}
static void remove_buf(struct iris_buffer **bufs,int *count,struct vb2_v4l2_buffer *b) {
    for(int j=0;j<*count;j++) if(&bufs[j]->base.vb==b) {
        memmove(&bufs[j],&bufs[j+1],(size_t)(--*count-j)*sizeof(bufs[0]));return;
    }
    CHECK(false);
}
static void v4l2_m2m_src_buf_remove_by_buf(struct v4l2_m2m_ctx *m,struct vb2_v4l2_buffer *b) { remove_buf(m->src,&m->ns,b); }
static void v4l2_m2m_dst_buf_remove_by_buf(struct v4l2_m2m_ctx *m,struct vb2_v4l2_buffer *b) { remove_buf(m->dst,&m->nd,b); }
static u32 iris_v4l2_type_to_driver(u32 t) { return t==10?BUF_INPUT:BUF_OUTPUT; }
static void reinit_completion(int *c) { *c=0; }
static int iris_wait_for_session_response(struct iris_inst *i,bool flush) { (void)flush; if(!wait_status) i->reservation.closed=true; return wait_status; }
#define v4l2_m2m_for_each_dst_buf_safe(ctx,b,n) for(int _j=0;_j<(ctx)->nd && ((b)=&(ctx)->dst[_j]->base,(n)=NULL,1);_j++)

static int hfi_commands, hfi_stop_error;
static int iris_inst_change_sub_state(struct iris_inst *i,u32 clear,u32 set) { i->sub_state=(i->sub_state&~clear)|set;return 0; }
static int iris_inst_state_change_streamon(struct iris_inst *i,u32 p) { (void)i;(void)p;return 0; }
static int iris_inst_state_change_streamoff(struct iris_inst *i,u32 p) { (void)i;(void)p;return 0; }
static int iris_alloc_and_queue_input_int_bufs(struct iris_inst *i) { (void)i;return 0; }
static int iris_set_stage(struct iris_inst *i,u32 p) { (void)i;(void)p;return 0; }
static int iris_set_pipe(struct iris_inst *i,u32 p) { (void)i;(void)p;return 0; }
static void iris_vb2_buffer_done(struct iris_inst *i,struct iris_buffer *b) {
 if(b->type==BUF_INPUT) v4l2_m2m_src_buf_remove_by_buf(i->m2m_ctx,&b->base.vb);
 else v4l2_m2m_dst_buf_remove_by_buf(i->m2m_ctx,&b->base.vb);
 completed++;
}

struct file { struct iris_inst *inst; };
struct v4l2_requestbuffers { u32 count; };
enum v4l2_buf_type { MOCK_BUF_TYPE = 0 };
static int streamoff_cancelled, reqbufs_calls;
static struct iris_inst *iris_get_inst(struct file *f) { return f->inst; }
static int v4l2_m2m_ioctl_streamoff(struct file *f,void *h,enum v4l2_buf_type t) {
 (void)f;(void)h;(void)t;streamoff_cancelled++;return 0;
}
static int v4l2_m2m_ioctl_reqbufs(struct file *f,void *h,struct v4l2_requestbuffers *b) {
 (void)f;(void)h;(void)b;reqbufs_calls++;return 0;
}
