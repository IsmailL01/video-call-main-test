<template>
  <div class="min-h-screen flex items-center justify-center bg-white dark:bg-[#202124] p-4 font-sans">
    <!-- Google-style Login Card -->
    <div class="w-full max-w-[448px] p-8 sm:p-10 border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-[#202124] animate-fade-in">
      
      <!-- Header -->
      <div class="flex flex-col items-center mb-8 text-center">
        <!-- Google Meet like logo -->
        <svg class="w-10 h-10 text-blue-600 dark:text-blue-400 mb-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
        </svg>
        <h1 class="text-2xl font-normal text-gray-900 dark:text-white mb-2">Sign in</h1>
        <p class="text-base text-gray-600 dark:text-gray-400">to continue to Meet Clone</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <div class="relative">
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="Enter access password"
              class="block w-full px-4 py-3.5 border border-gray-300 dark:border-gray-600 rounded-md bg-transparent text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 sm:text-base transition-colors"
              :disabled="isLoading"
              required
            />
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="flex items-center justify-between pt-4">
          <p class="text-xs text-gray-500 dark:text-gray-400 max-w-[150px]">
            Secure video calling without registration
          </p>
          
          <button
            type="submit"
            :disabled="!password.trim() || isLoading"
            class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <span v-if="isLoading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Signing in...
            </span>
            <span v-else>Next</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGlobalStore } from '../stores/global'

const router = useRouter()
const globalStore = useGlobalStore()

const password = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  if (!password.value.trim()) return

  try {
    isLoading.value = true
    const result = await globalStore.login(password.value)

    if (result.success) {
      const redirectTo = new URLSearchParams(window.location.search).get('redirect') || '/'
      router.push(redirectTo)
    }
  } catch (error) {
    console.error('Login failed:', error)
  } finally {
    isLoading.value = false
  }
}
</script>
