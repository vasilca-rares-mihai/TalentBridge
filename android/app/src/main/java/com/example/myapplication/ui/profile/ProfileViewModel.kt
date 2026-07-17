package com.example.myapplication.ui.profile

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.Attribute
import com.example.myapplication.data.model.CountResponse
import com.example.myapplication.data.model.FootballClubData
import com.example.myapplication.data.network.RetrofitClient
import com.example.myapplication.ui.getRoleFromToken
import kotlinx.coroutines.launch

class ProfileViewModel : ViewModel() {
    var email by mutableStateOf("Se incarca...")
    var role by mutableStateOf("")

    var athlete by mutableStateOf<AthleteData?>(null)
    var attribute by mutableStateOf<Attribute?>(null)
    var football_club by mutableStateOf<FootballClubData?>(null)
    var infoPannel by mutableStateOf(CountResponse())


    fun loadAthleteData(token: String, id: Int) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.getUserInfo("Bearer $token", id)
                email = response.email
                role = response.role

                attribute =
                    RetrofitClient.coreApi.get_athlete_attribute("Bearer $token", id).firstOrNull()
                athlete = response.athlete
            } catch (e: Exception) {
                email = "Eroare: ${e.localizedMessage}"
            }
        }
    }

    fun loadFootballClubData(token: String) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.getFootballClubInfo("Bearer $token")
                email = response.email
                role = response.role

                football_club = response.football_club

            } catch (e: Exception) {
                email = "Eroare: ${e.localizedMessage}"
            }
        }
    }

    fun get_athlete_attributes(token: String, athlete_id: Int) {
        viewModelScope.launch {
            try {
                attribute = RetrofitClient.coreApi.get_athlete_attribute("Bearer $token", athlete_id).firstOrNull()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun onLogout(token: String) {
        viewModelScope.launch {
            try {
                RetrofitClient.authApi.logout("Bearer $token")
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun infoPannel(token: String) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.info_pannel("Bearer $token")

                if (response.isSuccessful) {
                    infoPannel = response.body() ?: CountResponse()
                } else {
                    android.util.Log.e("API_ADMIN", "Eroare: ${response.code()}")
                }
            } catch (e: Exception) {
                android.util.Log.e("API_ADMIN", "Request error: ${e.message}")
            }
        }
    }



}