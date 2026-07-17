package com.example.myapplication.ui.settings

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.UpdatePassword
import com.example.myapplication.data.model.AthleteUpdate
import com.example.myapplication.data.model.FootballClubData
import com.example.myapplication.data.model.LoginData
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch

class SettingsViewModel: ViewModel() {
    var email by mutableStateOf("")
    var changeEmailData by mutableStateOf(LoginData("", ""))
    var updated_password by mutableStateOf(UpdatePassword("", "", ""))

    var updateSuccess by mutableStateOf(false)


    var athlete by mutableStateOf<AthleteUpdate?>(null)
    var football_club by mutableStateOf<FootballClubData?>(null)



    fun update_email(token: String, newData: LoginData) {
        viewModelScope.launch{
            try {
                RetrofitClient.coreApi.update_email("Bearer $token", newData)
                updateSuccess = true
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    fun update_password(token: String, new_passowrd: UpdatePassword) {
        viewModelScope.launch{
            try {
                val result = RetrofitClient.coreApi.update_password("Bearer $token", new_passowrd)
                if (result.isSuccessful)
                    updateSuccess = true
            } catch(e: Exception) {
                e.printStackTrace()
            }

        }
    }

    fun update_athlete_info(token: String, athlete_info: AthleteUpdate) {
        viewModelScope.launch{
            try {
                RetrofitClient.coreApi.update_athlete_info("Bearer $token", athlete_info)
            } catch (e: Exception) {
                e.printStackTrace()
            }

        }
    }
    fun update_fc_info(token: String, fc_info: FootballClubData) {
        viewModelScope.launch{
            try {
                RetrofitClient.coreApi.update_football_club_info("Bearer $token", fc_info)
            } catch (e: Exception) {
                e.printStackTrace()
            }

        }
    }


    fun delete_athlete(token: String) {
        viewModelScope.launch{
            try {
                RetrofitClient.coreApi.delete_athlete("Bearer $token")
                updateSuccess = true
            } catch (e: Exception) {
                e.printStackTrace()
            }

        }
    }



    fun dataToupdate(token: String, athleteData: AthleteData?) {
        viewModelScope.launch{
            try {
                if (athleteData != null) {
                    athlete = AthleteUpdate(
                        first_name = athleteData.first_name,
                        second_name = athleteData.second_name,
                        field_position = athleteData.field_position,
                        weak_foot = athleteData.weak_foot,
                        height = athleteData.height,
                        weight = athleteData.weight,
                        country = athleteData.country,
                        region = athleteData.region,
                        city = athleteData.city,
                        phone_number = athleteData.phone_number,
                        date_of_birth = athleteData.date_of_birth
                    )
                }

            } catch (e: Exception) {
                e.printStackTrace()
            }


        }
    }


}