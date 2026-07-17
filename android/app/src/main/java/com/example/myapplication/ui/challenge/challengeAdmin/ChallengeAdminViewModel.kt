package com.example.myapplication.ui.challenge.challengeAdmin

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch

class ChallengeAdminViewModel : ViewModel() {

    var challenges by mutableStateOf<List<Challenge?>>(emptyList())


    fun loadChallenges(token: String) {
        viewModelScope.launch {
            try {
                challenges = RetrofitClient.coreApi.get_challenges("Bearer $token", 0).body() ?: emptyList()
            } catch (e: Exception) {

            }
        }
    }
    fun createChallenge(token: String, challenge: Challenge?) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.create_challenge("Bearer $token", challenge)
                if (response.isSuccessful) {
                    loadChallenges(token)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    fun deleteChallenge(token: String, challenge_id: Int) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.delete_challenge("Bearer $token", challenge_id)
                if (response.isSuccessful) {
                    loadChallenges(token)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

}