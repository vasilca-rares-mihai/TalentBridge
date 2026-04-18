package com.example.myapplication.ui.challenge.challengeInfo

import android.content.Context
import android.net.Uri
import androidx.compose.runtime.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.data.network.RetrofitClient
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

    fun loadChallengeInfo(context: Context, token: String, challenge: Challenge, videoUri: Uri) {
        viewModelScope.launch {
            try {


                uploadStatus = "Preparing video..."
                val file = getFileFromUri(context, videoUri) ?: return@launch

                uploadStatus = "Uploading..."
                val requestFile = RequestBody.create(MediaType.parse("video/*"), file)
                val videoPart = MultipartBody.Part.createFormData("file", file.name, requestFile)

                val response = RetrofitClient.coreApi.upload_video("Bearer $token", challenge.id_challenge, videoPart)

                if (response.isSuccessful) {
                    uploadStatus = "Upload successful! You can start analysis."
                } else {
                    uploadStatus = "Upload failed: ${response.code()}"
                }
                file.delete()
            } catch (e: Exception) {
                uploadStatus = "Error: ${e.message}"
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


    fun start_analysis(token: String, challengeId: Int) {
        viewModelScope.launch {
            try {
                processedVideoUrl = null
                uploadStatus = "Starting analysis for challenge $challengeId..."

                val response = RetrofitClient.coreApi.analyze_video("Bearer $token", challengeId)

                if (response.isSuccessful) {
                    uploadStatus = "Analysis in progress... Please wait."
                    pollAnalysisStatus(token, challengeId)
                } else {
                    uploadStatus = "Analysis failed to start: ${response.code()}"
                }
            } catch (e: Exception) {
                uploadStatus = "Error: ${e.message}"
            }
        }
    }

    private suspend fun pollAnalysisStatus(token: String, challengeId: Int) {
        var isComplete = false
        while (!isComplete) {
            delay(5000)
            try {
                val statusResponse = RetrofitClient.coreApi.check_analysis_status("Bearer $token", challengeId)

                if (statusResponse.isSuccessful) {
                    val status = statusResponse.body()?.status

                    if (status == "completed") {
                        isComplete = true
                        uploadStatus = "Analysis complete!"
                        processedVideoUrl = "${RetrofitClient.CORE_URL}api/athlete/video/display/$challengeId"
                    } else if (status == "failed") {
                        isComplete = true
                        uploadStatus = "Analysis failed during processing."
                    } else {
                        uploadStatus = "Analysis is currently: $status... Please wait."
                    }
                }
            } catch (e: Exception) {
            }
        }
    }


}