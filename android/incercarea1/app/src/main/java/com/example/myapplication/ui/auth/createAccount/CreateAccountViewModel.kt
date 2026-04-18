package com.example.myapplication.ui.auth.createAccount

import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.AccountType
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.CreateAthleteRequest
import com.example.myapplication.data.model.CreateFootballClubRequest
import com.example.myapplication.data.model.FootballClubData
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch
import java.util.Date

class CreateAccountViewModel : ViewModel() {
    var email by mutableStateOf("")
    var password by mutableStateOf("")
    var athleteInfo by mutableStateOf(AthleteData(0, "", "", 0, "", "", "", 0f, 0f, "", "", "", "", Date()))

    var football_clubInfo by mutableStateOf(FootballClubData())

    var errorMessage by mutableStateOf<String?>(null)
    var isLoading by mutableStateOf(false)

    fun createAccount(selectedAccountType: AccountType, onSuccess: () -> Unit) {
        if(email.isBlank() || password.isBlank() ) {
            errorMessage = "Uncompleted fields!"
            Log.e("VALIDATION", errorMessage!!)
            return
        }

        errorMessage = null
        isLoading = true

        // athlete
        val finalAthleteData = athleteInfo.copy(field_position = athleteInfo.field_position.lowercase(),
            weak_foot = athleteInfo.weak_foot.lowercase(),
            gender = athleteInfo.gender.replaceFirstChar { it.uppercase() }
        )

        val requestBody = CreateAthleteRequest(
            email = email,
            password = password,
            athlete_data = finalAthleteData
        )
        val requestBodyFootballClub = CreateFootballClubRequest(
            email = email,
            password = password,
            club_data = football_clubInfo
        )

        viewModelScope.launch {
            try {
                val registerResponse = if (selectedAccountType == AccountType.athlete) {
                    RetrofitClient.authApi.create_athlete(requestBody)
                } else {
                    RetrofitClient.authApi.create_football_club(requestBodyFootballClub)
                }

                if (registerResponse.isSuccessful) {
                    isLoading = false
                    onSuccess()
                } else {
                    isLoading = false
                    val errorBody = registerResponse.errorBody()?.string() ?: ""
                    Log.e("API_ERROR", "Server error: $errorBody")
                    if (registerResponse.code() == 400 || registerResponse.code() == 409) {
                        if (errorBody.contains("email", ignoreCase = true) || errorBody.contains("already", ignoreCase = true)) {
                            errorMessage = "This email is already in use. Try logging in!"
                        } else {
                             errorMessage = "Invalid data. Please check the fields."
                        }
                    } else {
                        errorMessage = "An error occurred (Cod: ${registerResponse.code()}). Try again."
                    }
                }
            } catch (e: Exception){
                isLoading = false
                errorMessage = "Auth error: ${e.localizedMessage}"
            }

        }
    }
}