package com.example.myapplication.ui.fc_search_athlete

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.AthleteFilters
import com.example.myapplication.data.model.Attribute
import com.example.myapplication.data.model.FcFilters
import com.example.myapplication.data.model.FootballClubData
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch
import kotlin.collections.plus

class SearchViewModel : ViewModel() {

    var athleteFilters by mutableStateOf(AthleteFilters())
    var fcFilters by mutableStateOf(FcFilters())

    var athletes by mutableStateOf<List<AthleteData>>(emptyList())
    var football_clubs by mutableStateOf<List<FootballClubData>>(emptyList())

    var athlete_attributes by mutableStateOf<Attribute?>(null)

    var compareList by mutableStateOf<List<AthleteData?>>(emptyList())

    var athlete1_attributes by mutableStateOf<Attribute?>(null)
    var athlete2_attributes by mutableStateOf<Attribute?>(null)

    fun performAthleteSearch(token: String) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.search_athletes("Bearer $token", athleteFilters)
                if (response.isSuccessful) {
                    athletes = response.body() ?: emptyList()
                } else {
                    val errorJson = response.errorBody()?.string()
                    println("Eroare 422 de la server: $errorJson")
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun performFCSearch(token: String) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.search_fc("Bearer $token", fcFilters)
                if (response.isSuccessful) {
                    football_clubs = response.body() ?: emptyList()
                } else {
                    val errorJson = response.errorBody()?.string()
                    println("Eroare 422 de la server: $errorJson")
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    fun get_athlete_attributes(token: String, athlete_id: Int) {
        viewModelScope.launch {
            try {
                athlete_attributes = RetrofitClient.coreApi.get_athlete_attribute("Bearer $token", athlete_id).firstOrNull()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    fun get_athlete_attributes_for_comp(token: String, athlete_id1: Int, athlete_id2: Int) {
        viewModelScope.launch {
            try {
                athlete1_attributes = RetrofitClient.coreApi.get_athlete_attribute("Bearer $token", athlete_id1).firstOrNull()
                athlete2_attributes = RetrofitClient.coreApi.get_athlete_attribute("Bearer $token", athlete_id2).firstOrNull()

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    fun addToCOmapre(athlete: AthleteData) {
        viewModelScope.launch {
            try {
                if (compareList.size < 2) {
                    compareList = compareList + athlete

                } else {
                    compareList = compareList.drop(1) + athlete
                }

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun rmFromComapre(athlete: AthleteData) {
        viewModelScope.launch {
            try {
                compareList = compareList - athlete
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }


    fun delete_user(token: String, userId: Int, isAthlete: Boolean) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.delete_account("Bearer $token", userId)

                if (response.isSuccessful) {
                    if (isAthlete) {
                        performAthleteSearch(token)
                    } else {
                        performFCSearch(token)
                    }
                } else {
                    android.util.Log.e("FAIL", "Failed to delete: ${response.code()}")
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}