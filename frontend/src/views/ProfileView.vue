<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { uploadMyAvatar } from '@/api/modules/users'
import { getMySubmissions } from '@/api/modules/submissions'
import type { Submission } from '@/types/submission'

import { useAuthStore } from '@/stores/auth'
import { formatUid } from '@/utils/formatUid'


const router = useRouter()

const authStore = useAuthStore()


const defaultAvatar = '/static/images/avatars/maodie.jpg'


const allowedAvatarTypes = new Set([
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/gif',
])


const maxAvatarSize = 2 * 1024 * 1024



const uploading = ref(false)

const error = ref('')

const success = ref('')



/*
|--------------------------------------------------------------------------
| 投稿
|--------------------------------------------------------------------------
*/


const mySubmissions = ref<Submission[]>([])

const submissionsLoading = ref(false)

const submissionsError = ref('')



const visibleSubmissions = computed(() => {

  return mySubmissions.value.slice(0, 6)

})



async function loadMySubmissions() {

  if (!authStore.isLoggedIn) {

    return

  }


  submissionsLoading.value = true

  submissionsError.value = ''



  try {

    const response = await getMySubmissions()

    mySubmissions.value = response.data


  } catch (err) {

    console.error(
      '加载投稿失败',
      err
    )

    submissionsError.value =
      '投稿内容加载失败'


  } finally {

    submissionsLoading.value = false

  }

}




onMounted(() => {

  loadMySubmissions()

})





/*
|--------------------------------------------------------------------------
| 头像
|--------------------------------------------------------------------------
*/


const avatarPreview = computed(() => {

  return (
    authStore.user?.avatar_url
    ||
    defaultAvatar
  )

})



function getErrorMessage(
  reason: unknown,
  fallback: string
) {

  if (
    axios.isAxiosError<{detail?:string}>(reason)
  ) {

    return (
      reason.response?.data?.detail
      ||
      fallback
    )

  }


  return fallback

}




async function handleAvatarChange(
  event: Event
) {

  const input =
    event.target as HTMLInputElement


  const file =
    input.files?.[0]


  if (!file) {

    return

  }



  error.value = ''

  success.value = ''



  if (
    !allowedAvatarTypes.has(file.type)
  ) {

    error.value =
      '头像只支持 jpg、png、webp、gif 格式'

    input.value=''

    return

  }



  if (
    file.size > maxAvatarSize
  ) {

    error.value =
      '头像文件不能超过 2MB'

    input.value=''

    return

  }




  uploading.value=true



  try {

    const response =
      await uploadMyAvatar(file)


    authStore.setUser(
      response.data
    )


    success.value =
      '头像更新成功'


  } catch(reason:unknown) {


    error.value =
      getErrorMessage(
        reason,
        '头像上传失败'
      )


  } finally {

    uploading.value=false

    input.value=''

  }

}





function formatDate(
  value:string
){

  const date =
    new Date(value)


  return date.toLocaleDateString(
    'zh-CN',
    {
      year:'numeric',
      month:'2-digit',
      day:'2-digit'
    }
  )

}

function getFileUrl(url: string) {
  if (!url) {
    return ''
  }

  if (url.startsWith('http')) {
    return url
  }

  return `http://localhost:8000${url}`
}




function goLogin(){

  router.push('/login')

}

</script>
<template>

  <main class="profile-page">


    <!-- 已登录 -->

    <section
      v-if="authStore.user"
      class="profile-card"
    >



      <!-- 用户信息 -->

      <div class="profile-header">


        <!-- 头像 -->

        <div class="avatar-wrapper">


          <img
            class="profile-avatar"
            :src="avatarPreview"
            :alt="authStore.user.username"
          />



          <!-- 修改头像按钮 -->

          <label
            class="avatar-edit-button"
            :class="{ disabled: uploading }"
            title="修改头像"
          >


            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >

              <path
                d="M15.232 5.232l3.536 3.536M4 20l4.121-.824L19.475 5.82a2.5 2.5 0 00-3.536-3.536L4.824 13.4 4 20z"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />

            </svg>



            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              :disabled="uploading"
              @change="handleAvatarChange"
            />

          </label>


        </div>




        <!-- 用户资料 -->


        <div>


          <p class="section-kicker">
            USER PROFILE
          </p>



          <h1>
            {{ authStore.user.username }}
          </h1>



          <p class="user-meta">

            UID
            {{ formatUid(authStore.user.id) }}

            ·

            哈气值
            {{ authStore.user.haki_value }}

          </p>


        </div>



      </div>





      <!-- 我的投稿 -->


      <section class="profile-content">


        <div class="content-header">


          <div>


            <p class="section-kicker">
              MY SUBMISSIONS
            </p>


            <h2>
              我的投稿
            </h2>


          </div>



          <span class="submission-count">

            {{ mySubmissions.length }}

            条

          </span>


        </div>





        <!-- 加载 -->


        <p
          v-if="submissionsLoading"
          class="submission-status"
        >

          正在翻找你的哈基米投稿...

        </p>





        <!-- 错误 -->


        <p
          v-else-if="submissionsError"
          class="submission-status submission-error"
        >

          {{ submissionsError }}

        </p>





        <!-- 空状态 -->


        <div
          v-else-if="mySubmissions.length === 0"
          class="submission-empty"
        >


          <div class="empty-icon">
            🐱
          </div>



          <h3>
            还没有投稿
          </h3>



          <p>
            去贡献一点哈基米内容吧。
          </p>




          <RouterLink
            to="/submit"
            class="submit-button"
          >

            去投稿 →

          </RouterLink>



        </div>





        <!-- 投稿列表 -->


        <div
          v-else
        >



          <div
            class="submission-list"
          >


            <article
              v-for="submission in visibleSubmissions"
              :key="submission.id"
              class="submission-card"
            >



              <!-- 预览 -->


              <div class="submission-preview">


                <!-- 表情包 -->


                <img
                  v-if="submission.submission_type === 'meme'"
                   :src="getFileUrl(submission.file_url)"
                  :alt="submission.title"
                />



                <!-- 音乐 -->


                <div
                  v-else
                  class="music-placeholder"
                >

                  ♪

                </div>



              </div>





              <!-- 信息 -->


              <div class="submission-info">



                <span class="submission-type">

                  {{
                    submission.submission_type === 'meme'
                    ? '表情包'
                    : '音乐'
                  }}

                </span>




                <h3>

                  {{ submission.title }}

                </h3>




                <p
                  v-if="submission.description"
                >

                  {{ submission.description }}

                </p>





                <div class="submission-meta">


                  <span>

                    投稿于
                    {{ formatDate(submission.created_at) }}

                  </span>



                  <a
                    :href="getFileUrl(submission.file_url)"
                    target="_blank"
                    rel="noopener noreferrer"
                  >

                    查看内容 →

                  </a>



                </div>




              </div>



            </article>




          </div>






          <!-- 第17.3步 -->

          <RouterLink
            v-if="mySubmissions.length > 6"
            to="/my-submissions"
            class="view-all-submissions"
          >

            查看全部投稿 →

          </RouterLink>




        </div>



      </section>






    </section>







    <!-- 未登录 -->


    <section
      v-else
      class="profile-card"
    >


      <p class="section-kicker">
        NOT LOGIN
      </p>



      <h1>
        你还没有登录
      </h1>



      <p class="user-meta">

        登录后可以上传头像、投稿表情包和积累哈气值。

      </p>



      <button
        type="button"
        class="login-button"
        @click="goLogin"
      >

        去登录

      </button>



    </section>



  </main>


</template>
<style scoped>

/*
|--------------------------------------------------------------------------
| 页面整体
|--------------------------------------------------------------------------
*/


.profile-page {

  max-width: 900px;

  margin: 0 auto;

  padding: 80px 24px 120px;

}




.profile-card {

  padding: 40px;


  border-radius: 36px;


  background: #fffaf0;


  box-shadow:
    0 24px 60px rgba(79,61,32,0.12);

}






/*
|--------------------------------------------------------------------------
| 用户信息
|--------------------------------------------------------------------------
*/


.profile-header {

  display:flex;

  align-items:center;

  gap:28px;

}




.avatar-wrapper {

  position:relative;

  flex:0 0 auto;

}




.profile-avatar {

  display:block;


  width:120px;

  height:120px;


  border:4px solid #f6c534;


  border-radius:50%;


  object-fit:cover;


  background:#fffdf7;

}






/*
|--------------------------------------------------------------------------
| 修改头像按钮
|--------------------------------------------------------------------------
*/


.avatar-edit-button {


  position:absolute;


  left:-2px;


  bottom:3px;



  display:grid;

  place-items:center;



  width:38px;

  height:38px;



  border:3px solid #fffaf0;


  border-radius:50%;



  background:#f6c534;


  color:#292722;



  box-shadow:

    0 6px 18px rgba(74,55,20,0.2);



  cursor:pointer;



  transition:

    transform .2s ease,

    box-shadow .2s ease;

}



.avatar-edit-button:hover {


  transform:scale(1.08);



  box-shadow:

    0 8px 22px rgba(74,55,20,0.26);

}



.avatar-edit-button svg {


  width:18px;

  height:18px;

}



.avatar-edit-button input {


  display:none;

}



.avatar-edit-button.disabled {


  opacity:.55;

  pointer-events:none;

}






/*
|--------------------------------------------------------------------------
| 标题
|--------------------------------------------------------------------------
*/


.section-kicker {


  margin:0 0 10px;


  color:#b88a12;


  font-size:13px;


  font-weight:800;


  letter-spacing:.12em;

}



.profile-card h1 {


  margin:0;


  color:#25231f;


  font-size:42px;


}



.user-meta {


  margin:12px 0 0;


  color:#7b6a4a;


  font-size:16px;


  font-weight:700;

}








/*
|--------------------------------------------------------------------------
| 我的投稿区域
|--------------------------------------------------------------------------
*/


.profile-content {


  margin-top:38px;


  padding:34px 36px;



  border:1px solid #eadfc9;


  border-radius:30px;



  background:
    rgba(255,253,248,.75);

}




.content-header {


  display:flex;


  align-items:flex-end;


  justify-content:space-between;


  gap:24px;



  margin-bottom:28px;

}



.content-header h2 {


  margin:0;


  color:#292722;


  font-size:30px;


  font-weight:900;

}





.submission-count {


  display:inline-flex;


  align-items:center;


  justify-content:center;



  padding:9px 16px;



  border-radius:999px;



  background:#fff1b8;



  color:#896712;



  font-size:14px;



  font-weight:900;

}







/*
|--------------------------------------------------------------------------
| 投稿列表
|--------------------------------------------------------------------------
*/


.submission-list {


  display:grid;


  gap:16px;

}




.submission-card {


  display:grid;



  grid-template-columns:

    100px

    minmax(0,1fr);



  gap:20px;



  padding:16px;



  border:1px solid #eee3cf;


  border-radius:24px;



  background:#fffdf8;



  transition:

    transform .2s ease,

    box-shadow .2s ease;

}




.submission-card:hover {


  transform:translateY(-3px);



  box-shadow:

    0 14px 35px rgba(76,58,28,.08);

}





.submission-preview {


  overflow:hidden;



  width:100px;


  height:100px;



  border-radius:20px;



  background:

    linear-gradient(

      135deg,

      #fff1b8,

      #f8dbe5

    );

}



.submission-preview img {


  width:100%;


  height:100%;


  object-fit:cover;

}





.music-placeholder {


  display:grid;


  place-items:center;



  width:100%;


  height:100%;



  color:#292722;


  font-size:38px;


  font-weight:900;

}







.submission-info {


  min-width:0;

}



.submission-type {


  display:inline-flex;


  padding:5px 10px;



  border-radius:999px;



  background:#fff1ba;



  color:#927010;



  font-size:12px;



  font-weight:900;

}




.submission-info h3 {


  margin:10px 0 0;



  color:#292722;


  font-size:20px;


  font-weight:900;

}



.submission-info p {


  display:-webkit-box;



  margin:8px 0 0;



  overflow:hidden;



  color:#81745f;



  font-size:14px;



  line-height:1.7;



  -webkit-box-orient:vertical;


  -webkit-line-clamp:2;

}







.submission-meta {


  display:flex;


  align-items:center;


  justify-content:space-between;



  gap:16px;



  margin-top:14px;



  color:#a08a60;



  font-size:13px;



  font-weight:700;

}



.submission-meta a {


  color:#846318;


  font-weight:900;


  text-decoration:none;

}



.submission-meta a:hover {


  text-decoration:underline;

}








/*
|--------------------------------------------------------------------------
| 查看全部投稿按钮
|--------------------------------------------------------------------------
*/


.view-all-submissions {


  display:flex;


  justify-content:center;



  margin-top:24px;



  color:#846318;



  font-size:15px;



  font-weight:900;



  text-decoration:none;

}



.view-all-submissions:hover {


  text-decoration:underline;

}








/*
|--------------------------------------------------------------------------
| 空状态
|--------------------------------------------------------------------------
*/


.submission-empty {


  padding:60px 24px;



  border-radius:24px;



  background:#fffdf8;



  text-align:center;

}



.empty-icon {


  font-size:48px;

}



.submission-empty h3 {


  margin:16px 0 0;



  color:#292722;


  font-size:23px;


  font-weight:900;

}



.submission-empty p {


  margin:10px 0 0;



  color:#81745f;

}






.submit-button,


.login-button {


  display:inline-flex;


  align-items:center;


  justify-content:center;



  height:46px;



  margin-top:22px;



  padding:0 22px;



  border:0;


  border-radius:999px;



  background:#f6c534;



  color:#292722;



  font-weight:900;



  cursor:pointer;



  text-decoration:none;

}





.submit-button:hover {


  transform:translateY(-2px);

}







.submission-status {


  padding:50px 20px;



  color:#81745f;



  text-align:center;



  font-weight:700;

}



.submission-error {


  color:#c85b5b;

}








/*
|--------------------------------------------------------------------------
| 手机适配
|--------------------------------------------------------------------------
*/


@media(max-width:640px){



  .profile-page {


    padding:

      50px 18px 80px;

  }




  .profile-card {


    padding:24px;


    border-radius:28px;

  }





  .profile-header {


    flex-direction:column;


    align-items:flex-start;

  }





  .profile-avatar {


    width:96px;


    height:96px;

  }





  .avatar-edit-button {


    width:34px;


    height:34px;

  }





  .avatar-edit-button svg {


    width:16px;


    height:16px;

  }






  .profile-card h1 {


    font-size:34px;

  }





  .profile-content {


    padding:24px;


    border-radius:26px;

  }




  .content-header {


    flex-direction:column;


    align-items:flex-start;


    gap:12px;

  }





  .submission-card {


    grid-template-columns:

      76px

      minmax(0,1fr);



    gap:14px;


    padding:13px;

  }





  .submission-preview {


    width:76px;


    height:76px;


    border-radius:16px;

  }





  .submission-info h3 {


    font-size:17px;

  }





  .submission-meta {


    flex-direction:column;


    align-items:flex-start;


    gap:7px;

  }


}

</style>
