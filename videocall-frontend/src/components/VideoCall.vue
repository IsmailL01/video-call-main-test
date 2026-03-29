<template>
  <div class="min-h-screen bg-[#202124] flex flex-col font-sans relative overflow-hidden">
    
    <!-- Top Left Floating Status -->
    <div class="absolute top-4 left-4 z-20 flex items-center space-x-2 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-md text-white text-xs font-medium">
      <div :class="['w-2 h-2 rounded-full animate-pulse', connectionStatusColor]"></div>
      <span>{{ connectionStatusText }}</span>
    </div>

    <!-- Top Right Connection Quality -->
    <div
      v-if="connectionStats && showConnectionQuality"
      class="absolute top-4 right-4 z-20 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-md text-white text-xs font-medium flex items-center space-x-2"
    >
      <div
        :class="[
          'w-2.5 h-2.5 rounded-full',
          connectionQuality >= 80 ? 'bg-green-400' : connectionQuality >= 50 ? 'bg-yellow-400' : 'bg-red-400',
        ]"
      ></div>
      <span>{{ connectionQualityText }}</span>
    </div>

    <!-- Main Video Area -->
    <div class="flex-1 relative w-full h-full flex items-center justify-center p-4 pb-24">
      
      <!-- Remote Video (main) -->
      <div v-if="webrtcStore.hasRemoteVideo" class="w-full h-full relative rounded-xl overflow-hidden bg-black">
        <video
          ref="remoteVideoRef"
          autoplay
          playsinline
          class="w-full h-full object-contain"
          @loadedmetadata="onRemoteVideoLoaded"
        ></video>

        <!-- Remote video overlay info -->
        <div
          v-if="showVideoInfo"
          class="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm px-3 py-1.5 rounded-md text-white text-sm"
        >
          <p>{{ remoteVideoInfo }}</p>
        </div>
      </div>

      <!-- No remote video placeholder (Waiting Screen) -->
      <div v-else class="text-center text-white max-w-md mx-auto px-4">
        <h2 class="text-3xl font-normal mb-2">You're the only one here</h2>
        <p class="text-sm text-gray-400 mb-8">{{ waitingMessage || "Share this meeting link with others you want in the meeting" }}</p>
        
        <div class="bg-[#3c4043] rounded-md p-2 pl-4 flex items-center justify-between mb-4">
          <span class="font-medium tracking-wide text-gray-200 mr-4">{{ roomInfo?.short_code }}</span>
          <button
            @click="copyRoomCode"
            class="bg-transparent hover:bg-[#4a4d51] text-blue-400 p-2 rounded transition-colors"
            :title="roomCodeCopied ? 'Copied!' : 'Copy Code'"
          >
            <svg v-if="!roomCodeCopied" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
            <svg v-else class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Local Video (picture-in-picture) -->
      <div
        v-if="webrtcStore.hasLocalVideo"
        :class="[
          'absolute z-30 rounded-xl overflow-hidden shadow-2xl transition-all duration-300 cursor-pointer bg-[#3c4043]',
          localVideoSize === 'small' ? 'w-32 h-24 bottom-24 right-4' : localVideoSize === 'large' ? 'w-64 h-48 bottom-24 right-4' : 'w-48 h-36 bottom-24 right-4',
          !webrtcStore.isVideoEnabled ? 'border border-gray-700' : ''
        ]"
        @click="toggleLocalVideoSize"
      >
        <video
          ref="localVideoRef"
          autoplay
          muted
          playsinline
          class="w-full h-full object-cover"
          :class="{ mirror: shouldMirrorLocal, 'hidden': !webrtcStore.isVideoEnabled }"
        ></video>

        <!-- Camera off indicator -->
        <div
          v-if="!webrtcStore.isVideoEnabled"
          class="absolute inset-0 flex items-center justify-center bg-[#3c4043]"
        >
          <div class="w-12 h-12 rounded-full bg-[#5f6368] flex items-center justify-center text-white text-lg font-medium">
            You
          </div>
        </div>

        <!-- Muted indicator -->
        <div
          v-if="!webrtcStore.isAudioEnabled"
          class="absolute top-2 right-2 bg-black/60 backdrop-blur-sm rounded-full p-1.5"
        >
          <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1m0 0V7a3 3 0 013-3h8a3 3 0 013 3v2M4 9h1m11 0h5m-9 0a1 1 0 011-1v-1a1 1 0 011-1m-1 1v1a1 1 0 001 1M9 7h8a3 3 0 013 3v2"></path>
          </svg>
        </div>
      </div>
    </div>

    <!-- Connection message floating above bottom bar -->
    <div v-if="connectionMessage" class="absolute bottom-24 left-1/2 transform -translate-x-1/2 bg-black/60 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm z-20">
      {{ connectionMessage }}
    </div>

    <!-- Bottom Control Bar (Google Meet Style) -->
    <div class="absolute bottom-0 w-full h-20 bg-[#202124] flex items-center justify-between px-4 md:px-6 z-40">
      
      <!-- Left: Time & Room Code -->
      <div class="hidden md:flex items-center text-white text-base font-medium w-1/3">
        <span v-if="callDuration > 0">{{ utils.formatDuration(callDuration) }}</span>
        <span v-else>{{ new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
        <span class="mx-3 text-gray-500">|</span>
        <span>{{ roomInfo?.short_code }}</span>
      </div>

      <!-- Center: Main Controls -->
      <div class="flex items-center justify-center space-x-3 w-full md:w-1/3">
        <!-- Toggle Audio -->
        <button
          @click="webrtcStore.toggleAudio"
          :class="[
            'w-12 h-12 md:w-14 md:h-14 rounded-full flex items-center justify-center transition-colors',
            webrtcStore.isAudioEnabled ? 'bg-[#3c4043] hover:bg-[#4a4d51] text-white' : 'bg-[#ea4335] hover:bg-[#d93025] text-white'
          ]"
          :title="webrtcStore.isAudioEnabled ? 'Turn off microphone' : 'Turn on microphone'"
        >
          <svg v-if="webrtcStore.isAudioEnabled" class="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
          </svg>
          <svg v-else class="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1m0 0V7a3 3 0 013-3h8a3 3 0 013 3v2M4 9h1m11 0h5m-9 0a1 1 0 011-1v-1a1 1 0 011-1m-1 1v1a1 1 0 001 1M9 7h8a3 3 0 013 3v2"></path>
          </svg>
        </button>

        <!-- Toggle Video -->
        <button
          @click="webrtcStore.toggleVideo"
          :class="[
            'w-12 h-12 md:w-14 md:h-14 rounded-full flex items-center justify-center transition-colors',
            webrtcStore.isVideoEnabled ? 'bg-[#3c4043] hover:bg-[#4a4d51] text-white' : 'bg-[#ea4335] hover:bg-[#d93025] text-white'
          ]"
          :title="webrtcStore.isVideoEnabled ? 'Turn off camera' : 'Turn on camera'"
        >
          <svg v-if="webrtcStore.isVideoEnabled" class="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
          </svg>
          <svg v-else class="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18 21l-1.5-1.5m-6.364-6.364L8.5 14.5 7 13l1.636-1.636m0 0L9 10.5"></path>
          </svg>
        </button>

        <!-- End Call -->
        <button
          @click="handleEndCall"
          class="w-16 h-10 md:w-20 md:h-10 rounded-full bg-[#ea4335] hover:bg-[#d93025] flex items-center justify-center text-white transition-colors ml-2"
          title="Leave call"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M3 3l18 18"></path>
          </svg>
        </button>
      </div>

      <!-- Right: Secondary Controls -->
      <div class="flex items-center justify-end space-x-2 w-1/3">
        
        <!-- Info / Share -->
        <button
          @click="shareRoom"
          class="w-10 h-10 rounded-full hover:bg-[#3c4043] flex items-center justify-center text-white transition-colors"
          title="Meeting details"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </button>

        <!-- Participants -->
        <div class="relative flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#3c4043] text-white transition-colors cursor-pointer" title="People">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
          </svg>
          <span class="absolute top-1 right-0 bg-[#3c4043] text-xs rounded-full w-4 h-4 flex items-center justify-center">{{ participantCount }}</span>
        </div>

        <!-- More Options (Menu) -->
        <div class="relative">
          <button
            @click="showMenu = !showMenu"
            class="w-10 h-10 rounded-full hover:bg-[#3c4043] flex items-center justify-center text-white transition-colors"
            title="More options"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
            </svg>
          </button>

          <!-- Dropdown menu -->
          <div
            v-if="showMenu"
            v-click-outside="() => (showMenu = false)"
            class="absolute bottom-14 right-0 w-56 bg-white dark:bg-[#28292c] rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 py-2 z-50 mb-2"
          >
            <button
              @click="showStats = !showStats; showMenu = false"
              class="w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-[#3c4043] flex items-center space-x-3 transition-colors"
            >
              <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              <span>Connection stats</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Share Modal -->
    <Teleport to="body">
      <div
        v-if="showShareModal"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        @click="showShareModal = false"
      >
        <div class="bg-white dark:bg-[#202124] rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden animate-slide-up" @click.stop>
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-xl font-normal text-gray-900 dark:text-white">Meeting details</h3>
              <button @click="showShareModal = false" class="text-gray-500 hover:text-gray-700 dark:text-gray-400">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>
            
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Joining info
            </p>

            <div class="space-y-4">
              <!-- Link -->
              <div class="bg-gray-100 dark:bg-[#303134] rounded-md p-3 flex items-center justify-between">
                <span class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate pr-4">{{ roomLink }}</span>
                <button 
                  @click="copyRoomLink" 
                  class="text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 p-2 rounded-full transition-colors flex-shrink-0"
                  :title="roomLinkCopied ? 'Copied!' : 'Copy joining info'"
                >
                  <svg v-if="!roomLinkCopied" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                  <svg v-else class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                </button>
              </div>

              <!-- Code -->
              <div class="bg-gray-100 dark:bg-[#303134] rounded-md p-3 flex items-center justify-between">
                <span class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate pr-4">Code: {{ roomInfo?.short_code }}</span>
                <button 
                  @click="copyRoomCode" 
                  class="text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 p-2 rounded-full transition-colors flex-shrink-0"
                >
                  <svg v-if="!roomCodeCopied" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                  <svg v-else class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                </button>
              </div>

              <!-- QR Code -->
              <div v-if="qrCodeUrl" class="text-center pt-4">
                <div class="inline-block p-2 bg-white rounded-lg shadow-sm">
                  <img :src="qrCodeUrl" alt="Room QR Code" class="w-24 h-24" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Connection Stats Modal -->
    <Teleport to="body">
      <div
        v-if="showStats"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        @click="showStats = false"
      >
        <div class="bg-white dark:bg-[#202124] rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-slide-up max-h-[80vh] overflow-y-auto" @click.stop>
          <div class="p-6">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">Connection Statistics</h3>
              <button @click="showStats = false" class="text-gray-500 hover:text-gray-700 dark:text-gray-400">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>

            <div v-if="connectionStats" class="space-y-6 text-sm">
              <!-- Overall Quality -->
              <div class="flex justify-between items-center p-4 bg-gray-50 dark:bg-[#303134] rounded-xl">
                <span class="font-medium text-gray-900 dark:text-white">Overall Quality</span>
                <div class="flex items-center space-x-2">
                  <div :class="['w-3 h-3 rounded-full', connectionQuality >= 80 ? 'bg-green-400' : connectionQuality >= 50 ? 'bg-yellow-400' : 'bg-red-400']"></div>
                  <span class="text-gray-900 dark:text-white font-medium">{{ connectionQuality }}%</span>
                </div>
              </div>

              <!-- Video Stats -->
              <div v-if="connectionStats.video" class="border-t border-gray-200 dark:border-gray-700 pt-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-3 text-xs uppercase tracking-wider text-gray-500">Video</h4>
                <div class="space-y-3 text-gray-600 dark:text-gray-300">
                  <div class="flex justify-between"><span>Resolution</span><span class="font-mono">{{ videoResolution }}</span></div>
                  <div class="flex justify-between"><span>Frame Rate</span><span class="font-mono">{{ videoFrameRate }} fps</span></div>
                  <div class="flex justify-between"><span>Bitrate</span><span class="font-mono">{{ videoBitrate }} kbps</span></div>
                </div>
              </div>

              <!-- Audio Stats -->
              <div v-if="connectionStats.audio" class="border-t border-gray-200 dark:border-gray-700 pt-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-3 text-xs uppercase tracking-wider text-gray-500">Audio</h4>
                <div class="space-y-3 text-gray-600 dark:text-gray-300">
                  <div class="flex justify-between"><span>Bitrate</span><span class="font-mono">{{ audioBitrate }} kbps</span></div>
                </div>
              </div>

              <!-- Connection Stats -->
              <div v-if="connectionStats.connection" class="border-t border-gray-200 dark:border-gray-700 pt-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-3 text-xs uppercase tracking-wider text-gray-500">Network</h4>
                <div class="space-y-3 text-gray-600 dark:text-gray-300">
                  <div class="flex justify-between"><span>Round Trip Time</span><span class="font-mono">{{ roundTripTime }} ms</span></div>
                  <div class="flex justify-between"><span>Bandwidth</span><span class="font-mono">{{ bandwidth }} kbps</span></div>
                  <div class="flex justify-between"><span>Packet Loss</span><span class="font-mono">{{ packetLoss }}%</span></div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-8 text-gray-500">
              <p>No connection statistics available</p>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Full screen loading overlay -->
    <div
      v-if="isConnecting"
      class="fixed inset-0 bg-[#202124] flex items-center justify-center z-50"
    >
      <div class="text-center text-white">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-6"></div>
        <h3 class="text-2xl font-normal mb-2">{{ connectingMessage }}</h3>
        <p class="text-gray-400">{{ connectingSubMessage }}</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWebRTCStore } from '../stores/webrtc'
import { useRoomsStore } from '../stores/rooms'
import { useGlobalStore } from '../stores/global'
import { utils } from '../services/utils'
import { webrtcService } from '../services/webrtc'

const route = useRoute()
const router = useRouter()
const webrtcStore = useWebRTCStore()
const roomsStore = useRoomsStore()
const globalStore = useGlobalStore()

// Template refs
const localVideoRef = ref(null)
const remoteVideoRef = ref(null)

// Reactive state
const roomInfo = ref(null)
const callStartTime = ref(null)
const callDuration = ref(0)
const localVideoSize = ref('medium')
const showShareModal = ref(false)
const showStats = ref(false)
const showMenu = ref(false)
const roomCodeCopied = ref(false)
const roomLinkCopied = ref(false)
const shouldMirrorLocal = ref(true)
const showVideoInfo = ref(false)
const showConnectionQuality = ref(true)
const isConnecting = ref(false)
const connectingMessage = ref('Connecting...')
const connectingSubMessage = ref('Setting up your video call')

// Connection monitoring
const connectionStats = ref(null)
const statsMonitor = ref(null)

// Computed properties
const connectionStatusText = computed(() => {
  switch (webrtcStore.connectionState) {
    case 'new':
      return 'Initializing...'
    case 'connecting':
      return 'Connecting...'
    case 'connected':
      return 'Connected'
    case 'disconnected':
      return 'Disconnected'
    case 'failed':
      return 'Connection failed'
    case 'closed':
      return 'Connection closed'
    default:
      return 'Unknown'
  }
})

const connectionStatusColor = computed(() => {
  switch (webrtcStore.connectionState) {
    case 'connected':
      return 'bg-green-400'
    case 'connecting':
    case 'new':
      return 'bg-yellow-400'
    case 'disconnected':
    case 'failed':
    case 'closed':
      return 'bg-red-400'
    default:
      return 'bg-gray-400'
  }
})

const participantCount = computed(() => {
  return webrtcStore.remoteParticipants.length + 1 // +1 for local participant
})

const roomLink = computed(() => {
  if (roomInfo.value) {
    return `${window.location.origin}/join/${roomInfo.value.short_code}`
  }
  return ''
})

const qrCodeUrl = computed(() => {
  return roomInfo.value?.qr_code || null
})

const waitingMessage = computed(() => {
  const messages = [
    'Waiting for others to join...',
    'Room is ready for participants',
    'Share the code to get started',
  ]
  return messages[Math.floor(Date.now() / 5000) % messages.length]
})

const connectionMessage = computed(() => {
  if (webrtcStore.connectionState === 'connecting') {
    return 'Establishing secure connection...'
  } else if (webrtcStore.connectionState === 'failed') {
    return 'Connection failed. Please check your internet connection.'
  } else if (webrtcStore.connectionState === 'disconnected') {
    return 'Disconnected. Attempting to reconnect...'
  }
  return ''
})

// Connection quality computed properties
const connectionQuality = computed(() => {
  if (!connectionStats.value) return 0
  return webrtcService.calculateQuality(connectionStats.value)
})

const connectionQualityText = computed(() => {
  const quality = connectionQuality.value
  if (quality >= 80) return 'Excellent'
  if (quality >= 60) return 'Good'
  if (quality >= 40) return 'Fair'
  return 'Poor'
})

const videoResolution = computed(() => {
  if (connectionStats.value?.video?.inbound) {
    const { frameWidth, frameHeight } = connectionStats.value.video.inbound
    return `${frameWidth || 0}×${frameHeight || 0}`
  }
  return 'N/A'
})

const videoFrameRate = computed(() => {
  return connectionStats.value?.video?.inbound?.framesPerSecond || 0
})

const videoBitrate = computed(() => {
  if (connectionStats.value?.video?.inbound?.bytesReceived) {
    return Math.round(connectionStats.value.video.inbound.bytesReceived / 1000)
  }
  return 0
})

const audioBitrate = computed(() => {
  if (connectionStats.value?.audio?.inbound?.bytesReceived) {
    return Math.round(connectionStats.value.audio.inbound.bytesReceived / 1000)
  }
  return 0
})

const roundTripTime = computed(() => {
  const rtt = connectionStats.value?.connection?.currentRoundTripTime
  return rtt ? Math.round(rtt * 1000) : 0
})

const bandwidth = computed(() => {
  const bw = connectionStats.value?.connection?.availableOutgoingBitrate
  return bw ? Math.round(bw / 1000) : 0
})

const packetLoss = computed(() => {
  if (connectionStats.value?.video?.inbound) {
    const { packetsLost, packetsReceived } = connectionStats.value.video.inbound
    if (packetsReceived && packetsLost) {
      return Math.round((packetsLost / packetsReceived) * 100)
    }
  }
  return 0
})

const remoteVideoInfo = computed(() => {
  if (connectionStats.value?.video?.inbound) {
    const { frameWidth, frameHeight, framesPerSecond } = connectionStats.value.video.inbound
    return `${frameWidth}×${frameHeight} @ ${Math.round(framesPerSecond)}fps`
  }
  return ''
})

// Methods
const initializeCall = async () => {
  const roomId = route.params.roomId

  try {
    isConnecting.value = true
    connectingMessage.value = 'Finding room...'

    // Get room info
    const roomResult = await roomsStore.getRoomInfo(roomId)
    // if (!roomResult.success) {
    //   globalStore.addNotification('Room not found or expired', 'error')
    //   router.push('/')
    //   return
    // }

    roomInfo.value = roomResult.room
    connectingMessage.value = 'Accessing camera and microphone...'
    connectingSubMessage.value = 'Please allow permissions when prompted'

    // Initialize media
    const mediaResult = await webrtcStore.initializeLocalMedia()
    if (!mediaResult.success) {
      globalStore.addNotification('Failed to access camera/microphone', 'error')
    }

    connectingMessage.value = 'Setting up connection...'
    connectingSubMessage.value = 'Preparing for video call'

    // Create peer connection
    const peerResult = webrtcStore.createPeerConnection()
    if (!peerResult.success) {
      throw new Error('Failed to create peer connection')
    }

    connectingMessage.value = 'Connecting to room...'
    connectingSubMessage.value = 'Almost ready'

    // Connect WebSocket with timeout
    try {
      await webrtcStore.connectWebSocket(roomId)
    } catch (error) {
      console.error('WebSocket connection failed:', error)
      globalStore.addNotification('Failed to connect to room. Please try again.', 'error')
      isConnecting.value = false
      return
    }

    // Start call timer and monitoring
    callStartTime.value = new Date()
    startStatsMonitoring()

    isConnecting.value = false
  } catch (error) {
    console.error('Failed to initialize call:', error)
    globalStore.addNotification('Failed to join call', 'error')
    isConnecting.value = false
    // router.push('/')
  }
}

const handleEndCall = async () => {
  try {
    // Show confirmation if call is active
    if (webrtcStore.isConnected) {
      const confirmed = confirm('Are you sure you want to end this call?')
      if (!confirmed) return
    }

    // Stop stats monitoring
    if (statsMonitor.value) {
      clearInterval(statsMonitor.value)
      statsMonitor.value = null
    }

    // End the call
    await webrtcStore.endCall()

    // Leave room
    if (roomInfo.value) {
      const callEndTime = new Date()
      const duration = Math.floor((callEndTime - callStartTime.value) / 1000)

      await roomsStore.leaveRoom(roomInfo.value.room_id)

      // Update history with call duration
      roomsStore.updateHistoryEntry(roomInfo.value.room_id, {
        duration: duration,
        status: 'completed',
        ended_at: callEndTime.toISOString(),
      })
    }

    // router.push('/')
  } catch (error) {
    console.error('Failed to end call properly:', error)
    // Force navigate even if there's an error
    // router.push('/')
  }
}

const toggleLocalVideoSize = () => {
  const sizes = ['small', 'medium', 'large']
  const currentIndex = sizes.indexOf(localVideoSize.value)
  const nextIndex = (currentIndex + 1) % sizes.length
  localVideoSize.value = sizes[nextIndex]
}

const shareRoom = () => {
  showShareModal.value = true
  showMenu.value = false
}

const copyRoomCode = async () => {
  if (roomInfo.value) {
    const result = await utils.copyToClipboard(roomInfo.value.short_code)
    if (result.success) {
      roomCodeCopied.value = true
      globalStore.addNotification('Room code copied!', 'success', 2000)
      setTimeout(() => {
        roomCodeCopied.value = false
      }, 2000)
    }
  }
}

const copyRoomLink = async () => {
  const result = await utils.copyToClipboard(roomLink.value)
  if (result.success) {
    roomLinkCopied.value = true
    globalStore.addNotification('Room link copied!', 'success', 2000)
    setTimeout(() => {
      roomLinkCopied.value = false
    }, 2000)
  }
}

const onRemoteVideoLoaded = () => {
  showVideoInfo.value = true
  setTimeout(() => {
    showVideoInfo.value = false
  }, 3000)
}

const startStatsMonitoring = () => {
  if (webrtcStore.peerConnection) {
    statsMonitor.value = webrtcService.createQualityMonitor(
      webrtcStore.peerConnection,
      (quality, stats) => {
        connectionStats.value = stats
      },
      2000, // Update every 2 seconds
    )
  }
}

// Watch for stream changes
watch(
  () => webrtcStore.localStream,
  (newStream) => {
    nextTick(() => {
      if (localVideoRef.value && newStream) {
        localVideoRef.value.srcObject = newStream
      }
    })
  },
  { immediate: true },
)

watch(
  () => webrtcStore.remoteStream,
  (newStream) => {
    nextTick(() => {
      if (remoteVideoRef.value && newStream) {
        remoteVideoRef.value.srcObject = newStream
      }
    })
  },
  { immediate: true },
)

// Update call duration
let durationInterval = null

const updateCallDuration = () => {
  if (callStartTime.value) {
    callDuration.value = Math.floor((new Date() - callStartTime.value) / 1000)
  }
}

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  },
}

// Lifecycle
onMounted(() => {
  initializeCall()
  durationInterval = setInterval(updateCallDuration, 1000)
})

onUnmounted(async () => {
  // Cleanup intervals
  if (durationInterval) {
    clearInterval(durationInterval)
  }
  if (statsMonitor.value) {
    clearInterval(statsMonitor.value)
  }

  // End call and leave room
  try {
    await webrtcStore.endCall()

    if (roomInfo.value) {
      await roomsStore.leaveRoom(roomInfo.value.room_id)
    }
  } catch (error) {
    console.error('Cleanup error:', error)
  }
})
</script>

<style scoped>
.mirror {
  transform: scaleX(-1);
}

.control-button {
  @apply p-4 rounded-full shadow-lg transition-all duration-200 hover:scale-105 active:scale-95;
}

.control-button-active {
  @apply bg-green-500 hover:bg-green-600 text-white;
}

.control-button-inactive {
  @apply bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200;
}

.control-button-danger {
  @apply bg-red-500 hover:bg-red-600 text-white;
}

/* Animations */
@keyframes bounce-gentle {
  0%,
  20%,
  50%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.animate-bounce-gentle {
  animation: bounce-gentle 2s ease-in-out infinite;
}

/* Responsive design */
@media (max-width: 768px) {
  .control-button {
    @apply p-3;
  }

  .control-button svg {
    @apply w-5 h-5;
  }
}

/* Safe area for mobile devices */
.safe-area-inset {
  padding-top: env(safe-area-inset-top);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
}
</style>
