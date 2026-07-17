package com.example.myapplication.ui.leaderboard

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.data.model.LeaderboardInfo
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch

class LeaderboardViewModel : ViewModel() {
    var challenges by mutableStateOf<List<Challenge?>>(emptyList())
    var topAthletes by mutableStateOf<List<LeaderboardInfo?>>(emptyList())
    var actualChallenge by mutableStateOf(0)
    fun loadLeaderboard(token: String, challenge_id: Int) {
        viewModelScope.launch {
            try {
                topAthletes = RetrofitClient.coreApi.get_leaderboard("Bearer $token", challenge_id).body() ?: emptyList()
                challenges = RetrofitClient.coreApi.get_challenges("Bearer $token", 0).body() ?: emptyList()

            } catch(e: Exception) {
            }
        }
    }

}