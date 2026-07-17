package com.example.myapplication.ui.challenge.challengeList

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch

class ChallengeListViewModel : ViewModel() {
    var challengesLocked by mutableStateOf<List<Challenge?>>(emptyList())
    var challengesUnlocked by mutableStateOf<List<Challenge?>>(emptyList())
    var challenges by mutableStateOf<List<Challenge?>>(emptyList())
    var completedIds by mutableStateOf<Set<Int>>(emptySet())

    fun loadChallenges(token: String) {
        viewModelScope.launch {
            try {
                challenges = RetrofitClient.coreApi.get_challenges("Bearer $token", 0).body() ?: emptyList()
                challengesLocked = RetrofitClient.coreApi.get_challenges("Bearer $token", 2).body() ?: emptyList()
                challengesUnlocked = RetrofitClient.coreApi.get_challenges("Bearer $token", 1).body() ?: emptyList()

                // ce a finalizat deja atletul (ca sa marcam in lista)
                val done = RetrofitClient.coreApi.get_completed_challenges("Bearer $token")
                if (done.isSuccessful) completedIds = (done.body() ?: emptyList()).toSet()
            } catch (e: Exception) {

            }
        }
    }
}