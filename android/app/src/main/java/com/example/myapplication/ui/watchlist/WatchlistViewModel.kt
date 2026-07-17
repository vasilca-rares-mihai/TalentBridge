package com.example.myapplication.ui.watchlist

import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch

class WatchlistViewModel : ViewModel() {
    var athletesWatchlist = mutableStateListOf<AthleteData>()
        private set

    fun get_watchlist(token: String) {
        viewModelScope.launch {
            try {
                val list = RetrofitClient.coreApi.getWatchlist("Bearer $token")
                athletesWatchlist.clear()
                athletesWatchlist.addAll(list.filterNotNull())
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun add_to_watchlist(token: String, athlete: AthleteData?) {
        if (athlete == null) return
        viewModelScope.launch {
            try {
                val result = RetrofitClient.coreApi.add_to_watchlist("Bearer $token", athlete.user_id)
                if (result.isSuccessful) {
                    if (!athletesWatchlist.any { it.user_id == athlete.user_id }) {
                        athletesWatchlist.add(athlete)
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun delete_from_watchlist(token: String, athlete: AthleteData?) {
        if (athlete == null) return
        viewModelScope.launch {
            try {
                val result = RetrofitClient.coreApi.delete_from_watchlist("Bearer $token", athlete.user_id)
                if (result.isSuccessful) {
                    athletesWatchlist.removeAll { it.user_id == athlete.user_id }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}