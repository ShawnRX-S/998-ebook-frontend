<template>
  <div class="loginPage">
    <el-card class="loginCard" shadow="never">
      <template #header>
        <div class="cardHeader">
          <div class="title">{{ headerTitle }}</div>
          <div class="sub">Privacy-preserving ebook demo</div>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="loginTabs">
        <el-tab-pane label="Login" name="login">
          <el-form :model="loginForm" label-position="top" class="loginForm" @submit.prevent>
            <el-form-item label="Username">
              <el-input
                v-model="loginForm.username"
                placeholder="Please enter username"
                autocomplete="username"
              />
            </el-form-item>

            <el-form-item label="Password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="Please enter password"
                show-password
                autocomplete="current-password"
              />
            </el-form-item>

            <el-form-item>
              <div class="actions">
                <el-button type="primary" :loading="submitting" @click="onLogin">
                  Login
                </el-button>
                <el-button :disabled="submitting" @click="onReset">
                  Reset
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Sign Up" name="register">
          <el-form :model="registerForm" label-position="top" class="loginForm" @submit.prevent>
            <el-form-item label="Username">
              <el-input
                v-model="registerForm.username"
                placeholder="Please choose a username"
                autocomplete="username"
              />
            </el-form-item>

            <el-form-item label="Password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="Please choose a password"
                show-password
                autocomplete="new-password"
              />
            </el-form-item>

            <el-form-item>
              <div class="actions">
                <el-button type="primary" :loading="signingUp" @click="onRegister">
                  Create Account
                </el-button>
                <el-button :disabled="signingUp" @click="switchToLogin">
                  Back to Login
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { login, register } from '../utils/authStore'

const router = useRouter()
const route = useRoute()

const activeTab = ref('login')
const submitting = ref(false)
const signingUp = ref(false)

const headerTitle = computed(() => (activeTab.value === 'register' ? 'Create your account' : 'Login'))

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: ''
})

function switchToLogin() {
  activeTab.value = 'login'
}

function onReset() {
  loginForm.username = ''
  loginForm.password = ''
}

function getRedirectTarget() {
  const r = route.query.redirect
  if (!r) return null
  return typeof r === 'string' ? r : String(r)
}

function onLogin() {
  const username = loginForm.username.trim()
  const password = loginForm.password

  if (!username) {
    ElMessage.warning('Please enter username')
    return
  }
  if (!password) {
    ElMessage.warning('Please enter password')
    return
  }

  submitting.value = true
  setTimeout(() => {
    try {
      const auth = login(username, password)
      submitting.value = false

      const redirect = getRedirectTarget()
      if (redirect) {
        router.push(redirect)
        return
      }

      router.push(auth.isAdmin ? '/admin/dashboard' : '/books')
      ElMessage.success('Login successful')
    } catch (e) {
      submitting.value = false
      ElMessage.warning(e?.message || 'Login failed')
    }
  }, 250)
}

function onRegister() {
  const username = registerForm.username.trim()
  const password = registerForm.password

  if (!username) {
    ElMessage.warning('Please choose a username')
    return
  }
  if (!password) {
    ElMessage.warning('Please choose a password')
    return
  }

  signingUp.value = true
  setTimeout(() => {
    try {
      register(username, password)
      signingUp.value = false
      ElMessage.success('Account created successfully')

      loginForm.username = username
      loginForm.password = password
      activeTab.value = 'login'
    } catch (e) {
      signingUp.value = false
      ElMessage.warning(e?.message || 'Registration failed')
    }
  }, 250)
}
</script>

<style scoped>
.loginPage {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
}

.loginCard {
  width: min(460px, 100%);
  border-radius: var(--radius);
}

.cardHeader .title {
  font-weight: 800;
  font-size: 18px;
  letter-spacing: -0.01em;
}

.cardHeader .sub {
  margin-top: 4px;
  color: var(--muted);
  font-size: 13px;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  width: 100%;
}

.actions :deep(.el-button) {
  width: 100%;
}

@media (max-width: 420px) {
  .actions {
    grid-template-columns: 1fr;
  }
}
</style>

