"""Add unchanged VB2/M2M control flow and actual Iris cleanup callbacks.

Memory allocators, scheduling, firmware responses, provider APIs and OS types
are explicit mocks. No VB2 ownership/start/cancel body is reimplemented.
"""
import hashlib
import re
import subprocess
from pathlib import Path


def extend(root, ref, setup, slices, sources, extracted, read, take, function):
    def source(path):
        data = subprocess.check_output(['git', '-C', str(root), 'show', ref + ':' + path]) if ref else (root / path).read_bytes()
        sources[path] = data
        return data.decode()

    def functions(path, names):
        code = source(path)
        result = []
        for name in names.split():
            text = function(code, name)
            extracted[name] = hashlib.sha256(text.encode()).hexdigest()
            result.append(text)
        return '\n'.join(result)

    vb2_header = source('include/media/videobuf2-core.h')
    vb2_enum = re.search(r'enum vb2_buffer_state \{.*?\};', vb2_header, re.S).group()
    setup = setup.replace('#define VB2_BUF_STATE_ERROR 5\n#define VB2_BUF_STATE_DONE 4', vb2_enum)
    state = read('iris_state.h')
    enums = '\n'.join(re.findall(r'enum iris_inst_(?:sub_)?state \{.*?\};', state, re.S))
    setup = setup.replace('#define IRIS_INST_ERROR 9', '').replace('#define IRIS_INST_INPUT_STREAMING 3', '')
    setup = re.sub(r'enum iris_inst_sub_state \{.*?\};', enums, setup, flags=re.S)
    setup = setup.replace('enum iris_buffer_type { BUF_INPUT, BUF_OUTPUT };', 'enum iris_buffer_type { BUF_INPUT, BUF_OUTPUT, BUF_DPB };')
    setup = setup.replace('static void mutex_unlock', 'static void mutex_destroy(struct mutex *m) { CHECK(!m->held); }\nstatic void mutex_unlock', 1)
    setup = setup.replace('struct device { struct iris_core *core; int pm_refs; };', 'struct device { struct iris_core *core; int pm_refs; int refs; };')
    setup = setup.replace('struct vb2_queue { struct iris_inst *inst; u32 type; bool streaming,error; };', '''struct vb2_buffer;
struct vb2_queue {
 struct iris_inst *inst; u32 type; bool streaming,error;
 bool start_streaming_called,uses_requests,uses_qbuf,waiting_for_buffers,is_output,last_buffer_dequeued,is_busy;
 unsigned max_num_buffers,queued_count,min_queued_buffers;
 int owned_by_drv_count,done_lock,done_wq;
 struct list_head queued_list,done_list;
 struct mutex mmap_lock;
 struct vb2_buffer *bufs[8];
};''')
    setup = setup.replace('struct vb2_buffer { struct vb2_queue *vb2_queue;', '''struct media_request { int lock,state; };
struct request_object { struct media_request *req; };
struct vb2_buffer {
 enum vb2_buffer_state state;
 struct list_head queued_entry,done_entry;
 struct request_object req_obj;
 struct media_request *request;
 bool prepared,copied_timestamp,firmware_owned;
 unsigned done_calls;
 struct vb2_queue *vb2_queue;''')
    setup = setup.replace('struct v4l2_m2m_ctx { struct iris_buffer *src[16],*dst[16]; int ns,nd; struct vb2_queue sq,dq; bool stopped; };', '''struct v4l2_m2m_ctx;
struct v4l2_m2m_dev { int job_spinlock; struct v4l2_m2m_ctx *curr_ctx; };
struct v4l2_m2m_queue_ctx { struct vb2_queue q; int rdy_spinlock,num_rdy; struct list_head rdy_queue; };
struct v4l2_m2m_ctx {
 struct iris_buffer *src[16],*dst[16]; int ns,nd;
 union {
  struct { struct v4l2_m2m_queue_ctx out_q_ctx,cap_q_ctx; };
  struct { struct vb2_queue sq; int unused0[2]; struct list_head unused1;
           struct vb2_queue dq; int unused2[2]; struct list_head unused3; };
 };
 bool stopped;
 struct v4l2_m2m_dev *m2m_dev;
 u32 job_flags;struct list_head queue;int finished;
};''')
    setup = setup.replace('struct mutex lock;\n    struct iris_core *core;', 'struct mutex lock,ctx_q_lock;\n    struct iris_core *core;')
    setup = setup.replace('sequence_cap;', 'sequence_cap,sequence_out;')
    setup = setup.replace('static void iris_vb2_buffer_done(', 'int iris_vb2_buffer_done(')
    setup = setup.replace('struct iris_inst {', 'struct completion { int done; };\nstruct iris_inst {')
    setup = setup.replace('int completion,fh;', 'struct completion completion,flush_completion;\n    int fh,ctrl_handler;\n    struct v4l2_m2m_dev *m2m_dev;')
    setup = setup.replace('static void reinit_completion(int *c) { *c=0; }', 'static void reinit_completion(struct completion *c) { c->done=0; }')
    setup = setup.replace('struct file { struct iris_inst *inst; };', 'struct v4l2_fh { struct v4l2_m2m_ctx *m2m_ctx; };\nstruct file { struct iris_inst *inst; struct v4l2_fh fh; };')
    # Replace only external boundaries; extracted framework bodies remain intact.
    mocked = ['iris_queue_buffer', 'v4l2_m2m_buf_done', 'iris_vb2_buffer_done',
              'v4l2_m2m_ioctl_streamoff', 'iris_wait_for_session_response',
              'iris_inst_state_change_streamon']
    for name in mocked:
        body = function(setup, name)
        setup = setup.replace(body, body[:body.index('{')].strip() + ';')
    setup = setup.replace('#define v4l2_m2m_for_each_src_buf_safe(ctx,b,n) for(int _i=0;_i<(ctx)->ns && ((b)=&(ctx)->src[_i]->base,(n)=NULL,1);_i++)', '#define v4l2_m2m_for_each_src_buf_safe(ctx,b,n) for(int _i=0;_i<(ctx)->ns && ((b)=&(ctx)->src[_i]->base,(n)=NULL,1);_i+=(_i<(ctx)->ns && &(ctx)->src[_i]->base==(b)))')
    setup = setup.replace('#define v4l2_m2m_for_each_dst_buf_safe(ctx,b,n) for(int _j=0;_j<(ctx)->nd && ((b)=&(ctx)->dst[_j]->base,(n)=NULL,1);_j++)', '#define v4l2_m2m_for_each_dst_buf_safe(ctx,b,n) for(int _j=0;_j<(ctx)->nd && ((b)=&(ctx)->dst[_j]->base,(n)=NULL,1);_j+=(_j<(ctx)->nd && &(ctx)->dst[_j]->base==(b)))')
    # Existing slices define policy ioctl wrappers too early for framework prototypes.
    tail = take('iris_vidc.c', 'iris_policy_streamoff iris_policy_reqbufs')
    assert slices[-1] == tail
    slices = slices[:-1]
    setup = setup.replace('static int v4l2_m2m_ioctl_streamoff(', 'int v4l2_m2m_ioctl_streamoff(')
    setup = setup.replace('int (*session_close)(struct iris_inst *);', 'int (*session_close)(struct iris_inst *);\n int (*session_set_config_params)(struct iris_inst *,u32);')
    setup += '\n' + (Path(__file__).with_name('cleanup-framework-mocks.h')).read_text()
    callbacks = take('iris_utils.c', 'iris_helper_buffers_done iris_wait_for_session_response') + '\n' + take('iris_buffer.c', 'iris_helper_find_buf iris_vb2_buffer_done') + '\n'
    if 'static int iris_start_streaming(' in read('iris_vb2.c'):
        callbacks += take('iris_vb2.c', 'iris_start_streaming iris_vb2_start_after_streamon') + '\n'
    callbacks += take('iris_vb2.c', 'iris_vb2_start_streaming iris_vb2_stop_streaming')
    callbacks += '\n' + take('iris_vdec.c', 'iris_vdec_streamon_input iris_vdec_streamon_output')
    callbacks += '\n' + take('iris_vidc.c', 'iris_remove_session iris_session_close iris_close')
    vb2_core = 'drivers/media/common/videobuf2/videobuf2-core.c'
    vb2_v4l2 = 'drivers/media/common/videobuf2/videobuf2-v4l2.c'
    m2m = 'drivers/media/v4l2-core/v4l2-mem2mem.c'
    framework = functions(vb2_core, 'vb2_buffer_done __enqueue_in_driver vb2_start_streaming __vb2_dqbuf __vb2_queue_cancel vb2_core_streamon vb2_core_streamoff vb2_core_queue_release')
    framework += '\n' + functions(vb2_v4l2, 'vb2_streamon vb2_streamoff vb2_queue_release')
    framework += '\n' + functions(m2m, 'v4l2_m2m_streamon v4l2_m2m_streamoff v4l2_m2m_ctx_release v4l2_m2m_ioctl_streamon v4l2_m2m_ioctl_streamoff')
    if 'static int iris_policy_streamon(' in read('iris_vidc.c'):
        tail = take('iris_vidc.c', 'iris_policy_streamon') + '\n' + tail
    else:
        assert re.search(r'\.vidioc_streamon\s*=\s*v4l2_m2m_ioctl_streamon', read('iris_vidc.c'))
        tail = '#define iris_policy_streamon v4l2_m2m_ioctl_streamon\n' + tail
    callbacks += '\n' + take('iris_hfi_gen2_response.c', 'iris_hfi_gen2_handle_session_close')
    cases = Path(__file__).with_name('consumer-policy-cases.c').read_text()
    fixture = cases[:cases.index('static void adapter_cases')]
    fixture = fixture.replace('return close_status;', 'close_calls++;return member(i)?close_status:-EINVAL;')
    fixture = fixture.replace('return hfi_stop_error;', 'stop_calls++;if(!member(i))return -EINVAL;if(!hfi_stop_error)clear_firmware(i);return hfi_stop_error;')
    fixture = fixture.replace('{&inst[i],10,true,false}', '{.inst=&inst[i],.type=10,.streaming=true}').replace('{&inst[i],9,true,false}', '{.inst=&inst[i],.type=9,.streaming=true}')
    fixture = fixture.replace('.session_close=close_mock,', '.session_close=close_mock,.session_set_config_params=hfi_mock,')
    setup = setup.replace('static int iris_wait_for_session_response(', 'int iris_wait_for_session_response(')
    setup += '\nstatic bool member(struct iris_inst *i);\nstatic void clear_firmware(struct iris_inst *i);\n'
    # Fixture prefix contains only types/objects/mock provider callbacks and reset.
    return setup, slices + [callbacks, framework, tail, fixture]
