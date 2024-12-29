import request from '@/utils/request'
import { baseURL } from '@/utils/request'

// ChatComponent.vue

// 上传chatid对应的文件路径
export const postUploadFileURL = () => `${baseURL}/fileset/uploadfiles/`

// 关联 ChatSet 和 FileSet
export const associateChatsetToFilesetAxios = ({ chatset_id, fileset_id }) =>
  request.post('/fileset/associate_chatset', { chatset_id, fileset_id })

// 获取files
export const getFilesAxios = (fileset_id) =>
  request.get(`/fileset/${fileset_id}`)

// 获取fileset_id 和 files
export const getFilesetIdAxios = ({
  appset_id,
  chat_id = null,
  is_test_mode = false
}) => request.post('/fileset', { appset_id, chat_id, is_test_mode })

// 删除指定文件
export const deleteFileByFileIdAxios = (file_id) =>
  request.delete(`/fileset/${file_id}`)
