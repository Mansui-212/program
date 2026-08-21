<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { uploadMyAvatar } from '@/api/modules/users'
import { getMySubmissions } from '@/api/modules/submissions'
import { getMyFavorites } from '@/api/modules/favorites'
import { withdrawMeme } from '@/api/modules/memes'
import { withdrawMusicTrack } from '@/api/modules/musicTracks'
import type { Submission } from '@/types/submission'
import type { Favorite } from '@/types/favorite'

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
const submissionNotice = ref('')
const withdrawingSubmissionId = ref<number | null>(null)

const activeContentTab = ref<'submissions' | 'favorites'>('submissions')
const myFavorites = ref<Favorite[]>([])
const favoritesLoading = ref(false)
const favoritesError = ref('')



const visibleSubmissions = computed(() => {

  // 管理员下架（以及旧版已物理删除）的内容不再出现在用户个人中心；
  // 用户主动撤回的内容则作为自己的投稿历史保留。
  return mySubmissions.value.filter((submission) => (
    !submission.content_deleted
      && submission.content_status !== 'removed'
  ))

})

const favoriteMemes = computed(() => (
  myFavorites.value.filter((favorite) => favorite.target_type === 'meme')
))

const favoriteMusic = computed(() => (
  myFavorites.value.filter((favorite) => favorite.target_type === 'music')
))



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

async function loadMyFavorites() {

  if (!authStore.isLoggedIn) {

    return

  }

  favoritesLoading.value = true
  favoritesError.value = ''

  try {

    const response = await getMyFavorites()
    myFavorites.value = response.data

  } catch (err) {

    console.error('加载收藏内容失败', err)
    favoritesError.value = '收藏内容加载失败'

  } finally {

    favoritesLoading.value = false

  }
}

function getContentStatusLabel(submission: Submission) {
  if (submission.content_deleted || submission.content_status === 'removed') {
    return '管理员下架'
  }

  if (submission.content_status === 'withdrawn') {
    return '已撤回'
  }

  return '已发布'
}

function canWithdrawSubmission(submission: Submission) {
  return Boolean(
    submission.content_id
      && !submission.content_deleted
      && submission.content_status === 'active',
  )
}

async function withdrawSubmission(submission: Submission) {
  if (!submission.content_id || !canWithdrawSubmission(submission)) return

  const confirmed = window.confirm(
    `确定撤回“${submission.title}”吗？撤回后将不再公开显示，但会保留在你的投稿历史与管理员记录中。`,
  )
  if (!confirmed) return

  submissionsError.value = ''
  submissionNotice.value = ''
  withdrawingSubmissionId.value = submission.id

  try {
    if (submission.submission_type === 'meme') {
      await withdrawMeme(submission.content_id)
    } else {
      await withdrawMusicTrack(submission.content_id)
    }

    submission.content_status = 'withdrawn'
    submissionNotice.value = `已撤回“${submission.title}”。哈气值与历史记录不会受到影响。`
  } catch (reason) {
    console.error('撤回投稿失败', reason)
    submissionsError.value = getErrorMessage(reason, '撤回失败，请稍后重试。')
  } finally {
    withdrawingSubmissionId.value = null
  }
}




onMounted(() => {

  loadMySubmissions()
  loadMyFavorites()

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

  return url
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





      <div class="profile-tabs" role="tablist" aria-label="个人内容">
        <button
          type="button"
          :class="{ active: activeContentTab === 'submissions' }"
          @click="activeContentTab = 'submissions'"
        >
          我的投稿
        </button>
        <button
          type="button"
          :class="{ active: activeContentTab === 'favorites' }"
          @click="activeContentTab = 'favorites'"
        >
          我的收藏
        </button>
      </div>

      <!-- 我的投稿 -->
      <section v-if="activeContentTab === 'submissions'" class="profile-content">


        <div class="content-header">


          <div>


            <p class="section-kicker">
              MY SUBMISSIONS
            </p>


            <h2>
              我的投稿
            </h2>


          </div>



          <div class="content-actions">
            <span class="submission-count">

              {{ visibleSubmissions.length }}

              条

            </span>

            <RouterLink to="/profile/submissions" class="manage-submissions">
              查看所有投稿 →
            </RouterLink>

            <RouterLink to="/submit" class="manage-submissions">
              编辑投稿 →
            </RouterLink>
          </div>


        </div>


        <p class="withdraw-hint">
          已发布的作品可随时撤回。撤回后不再公开展示，但会保留在你的投稿历史中。
        </p>





        <p
          v-if="submissionNotice"
          class="submission-status submission-success"
        >

          {{ submissionNotice }}

        </p>

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
          v-else-if="visibleSubmissions.length === 0"
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



                <div class="submission-badges">

                  <span class="submission-type">

                  {{
                    submission.submission_type === 'meme'
                    ? '表情包'
                    : '音乐'
                  }}

                  </span>

                  <span
                    class="submission-state"
                    :class="submission.content_status"
                  >
                    {{ getContentStatusLabel(submission) }}
                  </span>

                </div>




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
                    v-if="submission.content_status === 'active' && !submission.content_deleted"
                    :href="getFileUrl(submission.file_url)"
                    target="_blank"
                    rel="noopener noreferrer"
                  >

                    查看内容 →

                  </a>

                  <span v-else>
                    该作品仅保留在投稿历史中
                  </span>

                  <button
                    v-if="canWithdrawSubmission(submission)"
                    type="button"
                    class="withdraw-button"
                    :disabled="withdrawingSubmissionId === submission.id"
                  @click="withdrawSubmission(submission)"
                  >
                    {{ withdrawingSubmissionId === submission.id ? '撤回中...' : '↶ 撤回作品' }}
                  </button>



                </div>




              </div>



            </article>




          </div>


        </div>



      </section>

      <section v-else class="profile-content">
        <div class="content-header">
          <div>
            <p class="section-kicker">MY FAVORITES</p>
            <h2>我的收藏</h2>
          </div>
          <span class="submission-count">{{ myFavorites.length }} 条</span>
        </div>

        <p v-if="favoritesLoading" class="submission-status">正在整理你的收藏...</p>
        <p v-else-if="favoritesError" class="submission-status submission-error">{{ favoritesError }}</p>

        <div v-else-if="myFavorites.length === 0" class="submission-empty">
          <div class="empty-icon">☆</div>
          <h3>还没有收藏</h3>
          <p>在表情包详情或音乐馆点一下收藏，喜欢的内容会出现在这里。</p>
          <RouterLink to="/memes" class="submit-button">去看看表情包 →</RouterLink>
        </div>

        <div v-else class="favorite-groups">
          <section class="favorite-group">
            <h3>收藏的表情包</h3>
            <p v-if="favoriteMemes.length === 0" class="favorite-empty">还没有收藏表情包。</p>
            <a
              v-for="favorite in favoriteMemes"
              :key="favorite.id"
              class="favorite-meme"
              :href="favorite.image_url || '#'"
              target="_blank"
              rel="noopener noreferrer"
            >
              <img :src="favorite.image_url || '/static/images/avatars/maodie.jpg'" :alt="favorite.title" />
              <span>{{ favorite.title }}</span>
            </a>
          </section>

          <section class="favorite-group">
            <h3>收藏的音乐</h3>
            <p v-if="favoriteMusic.length === 0" class="favorite-empty">还没有收藏音乐。</p>
            <article v-for="favorite in favoriteMusic" :key="favorite.id" class="favorite-track">
              <img v-if="favorite.cover_url" :src="favorite.cover_url" :alt="favorite.title" />
              <span v-else class="music-placeholder">♪</span>
              <div>
                <strong>{{ favorite.title }}</strong>
                <p>{{ favorite.author_name || '未知作者' }}</p>
              </div>
              <audio :src="favorite.audio_url || ''" controls preload="metadata" />
            </article>
          </section>
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


.profile-tabs {

  display:flex;

  flex-wrap:wrap;

  gap:10px;

  margin-top:38px;

}


.profile-tabs button {

  min-height:42px;

  padding:0 18px;

  border:1px solid #eadfc9;

  border-radius:999px;

  background:#fffdf7;

  color:#6f6047;

  font:inherit;

  font-size:14px;

  font-weight:900;

  cursor:pointer;

}


.profile-tabs button.active {

  border-color:#f6c534;

  background:#f6c534;

  color:#3b301b;

}


.profile-tabs + .profile-content {

  margin-top:14px;

}


.favorite-groups {

  display:grid;

  gap:22px;

}


.favorite-group {

  padding:22px;

  border:1px solid #eadfc9;

  border-radius:24px;

  background:#fffdf7;

}


.favorite-group > h3 {

  margin:0 0 15px;

  color:#302d27;

  font-size:18px;

}


.favorite-empty {

  margin:0;

  color:#8c7b5c;

  font-size:14px;

  font-weight:700;

}


.favorite-meme {

  display:grid;

  grid-template-columns:70px minmax(0,1fr);

  align-items:center;

  gap:14px;

  min-height:80px;

  margin-top:10px;

  padding:7px;

  border-radius:18px;

  color:#423921;

  font-size:15px;

  font-weight:850;

  text-decoration:none;

}


.favorite-meme:hover {

  background:#fff3c8;

}


.favorite-meme img {

  width:70px;

  height:70px;

  border-radius:14px;

  object-fit:cover;

  background:#f4ead7;

}


.favorite-track {

  display:grid;

  grid-template-columns:56px minmax(0,1fr);

  gap:14px;

  align-items:center;

  margin-top:10px;

  padding:12px;

  border-radius:18px;

  background:#fffaf0;

}


.favorite-track > img,
.favorite-track > .music-placeholder {

  display:grid;

  width:56px;

  height:56px;

  place-items:center;

  overflow:hidden;

  border-radius:14px;

  background:linear-gradient(135deg,#fff0bb,#ffdfe9);

  color:#6e5728;

  font-size:24px;

  object-fit:cover;

}


.favorite-track strong {

  color:#332f27;

  font-size:15px;

}


.favorite-track p {

  margin:5px 0 0;

  color:#8c7b5c;

  font-size:13px;

}


.favorite-track audio {

  grid-column:1 / -1;

  width:100%;

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

.content-actions {
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  justify-content:flex-end;
  gap:10px;
}

.manage-submissions {
  color:#846318;
  font-size:14px;
  font-weight:900;
  text-decoration:none;
}

.manage-submissions:hover {
  text-decoration:underline;
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

.submission-badges {

  display:flex;

  flex-wrap:wrap;

  gap:8px;

}

.submission-state {

  display:inline-flex;

  padding:5px 10px;

  border-radius:999px;

  background:#dff3dd;

  color:#397448;

  font-size:12px;

  font-weight:900;

}

.submission-state.withdrawn {

  background:#f0ece4;

  color:#746653;

}

.submission-state.removed {

  background:#ffe2e5;

  color:#a1424f;

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

.withdraw-hint {

  margin:12px 0 0;

  color:#8b7754;

  font-size:13px;

  line-height:1.65;

}

.withdraw-button {

  display:inline-flex;

  align-items:center;

  justify-content:center;

  min-height:34px;

  padding:0 13px;

  border:1px solid #e5b4b4;

  border-radius:999px;

  background:#fff1f1;

  color:#a44343;

  font:inherit;

  font-size:13px;

  font-weight:900;

  cursor:pointer;

  transition:
    background .2s ease,
    border-color .2s ease,
    transform .2s ease;

}

.withdraw-button:hover:not(:disabled) {

  border-color:#d66d6d;

  background:#ffe1e1;

  transform:translateY(-1px);

}

.withdraw-button:disabled {

  opacity:.55;

  cursor:not-allowed;

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

.submission-success {

  color:#3b8f52;

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
