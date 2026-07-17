package com.example.myapplication.ui.challenge.challengeInfo

import android.content.Context
import android.content.SharedPreferences
import android.net.Uri
import androidx.compose.runtime.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.data.network.RetrofitClient
import com.example.myapplication.data.network.TalentBridgeApi
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import okhttp3.MediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody
import java.io.File
import java.io.FileOutputStream

class ChallengeInfoViewModel : ViewModel() {

    var uploadStatus by mutableStateOf("")
    var processedVideoUrl by mutableStateOf<String?>(null)
    var analysisSummary by mutableStateOf<TalentBridgeApi.AnalysisSummary?>(null)
    var hasRawVideo by mutableStateOf(false)   // exista clip incarcat (gata de analiza)?

    // challenge-ul curent afisat (pt resetare/anti-race la schimbarea challenge-ului)
    private var currentChallengeId: Int = -1


    fun checkSavedVideo(context: Context, challengeId: Int, token: String) {
        // resetam imediat: nu aratam nimic ramas de la alt challenge / alt cont
        currentChallengeId = challengeId
        processedVideoUrl = null
        analysisSummary = null
        uploadStatus = ""
        hasRawVideo = false

        // adevarul vine din backend (per-user), nu din SharedPreferences (per-device)
        viewModelScope.launch {
            try {
                val s = RetrofitClient.coreApi.check_analysis_status("Bearer $token", challengeId)
                if (challengeId == currentChallengeId && s.isSuccessful && s.body()?.status == "completed") {
                    processedVideoUrl = "${RetrofitClient.CORE_URL}api/athlete/video/display/$challengeId"
                    uploadStatus = "Loaded previously analyzed video."
                    fetchSummary(token, challengeId)
                }
            } catch (_: Exception) { }

            // exista deja un clip incarcat? -> butonul de analiza ramane activ la reintrare
            try {
                val raw = RetrofitClient.coreApi.raw_video_exists("Bearer $token", challengeId)
                if (challengeId == currentChallengeId && raw.isSuccessful) {
                    hasRawVideo = (raw.body() == true)
                }
            } catch (_: Exception) { }
        }
    }

    private fun fetchSummary(token: String, challengeId: Int) {
        viewModelScope.launch {
            try {
                val resp = RetrofitClient.coreApi.get_summary("Bearer $token", challengeId)
                if (challengeId == currentChallengeId && resp.isSuccessful) {
                    analysisSummary = resp.body()
                }
            } catch (_: Exception) { }
        }
    }

    private fun saveVideoToMemory(context: Context, challengeId: Int, url: String) {
        val sharedPreferences: SharedPreferences = context.getSharedPreferences("ChallengePrefs", Context.MODE_PRIVATE)
        with(sharedPreferences.edit()) {
            putString("video_url_$challengeId", url)
            apply()
        }
        processedVideoUrl = url
    }


    fun loadChallengeInfo(context: Context, token: String, challenge: Challenge, videoUri: Uri) {
        val cid = challenge.id_challenge
        viewModelScope.launch {
            try {
                if (cid == currentChallengeId) uploadStatus = "Preparing video..."
                val file = getFileFromUri(context, videoUri) ?: return@launch

                if (cid == currentChallengeId) uploadStatus = "Uploading..."
                val requestFile = RequestBody.create(MediaType.parse("video/mp4"), file)
                val videoPart = MultipartBody.Part.createFormData("file", file.name, requestFile)

                val response = RetrofitClient.coreApi.upload_video("Bearer $token", cid, videoPart)

                // actualizam UI doar daca utilizatorul e inca pe acest challenge
                if (cid == currentChallengeId) {
                    if (response.isSuccessful) {
                        uploadStatus = "Upload successful! You can start analysis."
                        hasRawVideo = true
                    } else {
                        uploadStatus = "Upload failed: ${response.code()}"
                    }
                }
                file.delete()
            } catch (e: Exception) {
                if (cid == currentChallengeId) uploadStatus = "Error: ${e.message}"
            }
        }
    }

    fun clearVideoState() {
        processedVideoUrl = null
        uploadStatus = ""
    }

    private fun getFileFromUri(context: Context, uri: Uri): File? {
        return try {
            val inputStream = context.contentResolver.openInputStream(uri) ?: return null
            val tempFile = File(context.cacheDir, "temp_${System.currentTimeMillis()}.mp4")
            val outputStream = FileOutputStream(tempFile)
            inputStream.copyTo(outputStream)
            inputStream.close()
            outputStream.close()
            tempFile
        } catch (e: Exception) { null }
    }

    fun start_analysis(context: Context, token: String, challengeId: Int) {
        viewModelScope.launch {
            try {
                if (challengeId == currentChallengeId) {
                    processedVideoUrl = null
                    analysisSummary = null
                    uploadStatus = "Starting analysis for challenge $challengeId..."
                }

                val response = RetrofitClient.coreApi.analyze_video("Bearer $token", challengeId)

                if (response.isSuccessful) {
                    if (challengeId == currentChallengeId) uploadStatus = "Analysis in progress... Please wait."
                    pollAnalysisStatus(context, token, challengeId)
                } else {
                    if (challengeId == currentChallengeId) uploadStatus = "Analysis failed to start: ${response.code()}"
                }
            } catch (e: Exception) {
                if (challengeId == currentChallengeId) uploadStatus = "Error: ${e.message}"
            }
        }
    }

    private suspend fun pollAnalysisStatus(context: Context, token: String, challengeId: Int) {
        var isComplete = false
        while (!isComplete) {
            delay(5000)
            try {
                val statusResponse = RetrofitClient.coreApi.check_analysis_status("Bearer $token", challengeId)

                if (statusResponse.isSuccessful) {
                    val status = statusResponse.body()?.status
                    val esteCurent = (challengeId == currentChallengeId)

                    if (status == "completed") {
                        isComplete = true
                        // afisam rezultatul DOAR daca esti inca pe acest challenge
                        if (esteCurent) {
                            uploadStatus = "Analysis complete!"
                            processedVideoUrl = "${RetrofitClient.CORE_URL}api/athlete/video/display/$challengeId"
                            fetchSummary(token, challengeId)
                        }
                    } else if (status == "failed") {
                        isComplete = true
                        if (esteCurent) uploadStatus = "Analysis failed during processing."
                    } else {
                        if (esteCurent) uploadStatus = "Analysis is currently: $status... Please wait."
                    }
                }
            } catch (e: Exception) {
            }
        }
    }
}