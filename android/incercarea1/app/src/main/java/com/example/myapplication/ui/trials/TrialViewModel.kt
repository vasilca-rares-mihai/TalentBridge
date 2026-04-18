package com.example.myapplication.ui.trials

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshots.SnapshotStateList
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.Attribute
import com.example.myapplication.data.model.Trial
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch

class TrialViewModel: ViewModel() {

    var trials by mutableStateOf<List<Trial?>>(emptyList())

    var fc_my_trials = mutableStateListOf<Trial?>()
    var fc_trial_athletes by mutableStateOf<List<AthleteData?>>(emptyList())

    var athlete_trials_applications by mutableStateOf<List<Int>>(emptyList())


    var athlete_attributes by mutableStateOf<Attribute?>(null)
    var createdTrial by mutableStateOf<Trial?>(null)
    val athletesWatchlist = mutableStateListOf<AthleteData?>()



    fun loadTrials(token: String) {
        viewModelScope.launch {
            try {
                trials = RetrofitClient.coreApi.get_trials("Bearer $token").body() ?: emptyList()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun applyTrial(token: String, trialId: Int) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.apply_trial("Bearer $token", trialId)

                if (response.isSuccessful) {
                    athlete_trials_applications = athlete_trials_applications + trialId
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun my_trials_applications(token: String) {
        viewModelScope.launch {
            try {
                athlete_trials_applications =
                    RetrofitClient.coreApi.get_my_applications("Bearer $token").body()
                        ?: emptyList()

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun delete_trial_application(token: String, trialId: Int) {
        viewModelScope.launch {
            try {
                RetrofitClient.coreApi.delete_trial_application("Bearer $token", trialId)
                athlete_trials_applications = athlete_trials_applications - trialId
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun my_trials(token: String) {
        viewModelScope.launch {
            try {
                val list = RetrofitClient.coreApi.get_my_trials("Bearer $token")

                fc_my_trials.clear()
                fc_my_trials.addAll(list)

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun my_trial_applicants(token: String, trial_id: Int) {
        viewModelScope.launch {
            try {
                fc_trial_athletes = RetrofitClient.coreApi.get_trial_athletes("Bearer $token", trial_id).body() ?: emptyList()


            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun get_athlete_attributes(token: String, athlete_id: Int) {
        viewModelScope.launch {
            try {
                athlete_attributes =
                    RetrofitClient.coreApi.get_athlete_attribute("Bearer $token", athlete_id).firstOrNull()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun publish_trial(token: String, trial: Trial?) {
        if (trial == null) return

        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.publish_trial("Bearer $token", trial)

                if (response.isSuccessful) {
                    my_trials(token)

                } else {
                    println("Create trial error: ${response.errorBody()?.string()}")
                }
            } catch (e: Exception) {
                e.printStackTrace()
                my_trials(token)
            }
        }
    }

    fun delete_trial(token: String, trial_id: Int) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.coreApi.delete_trial("Bearer $token", trial_id)

                if (response.isSuccessful) {
                    fc_my_trials.removeAll { it?.id_trial == trial_id }
                } else {
                    println("Delete trial error: ${response.errorBody()?.string()}")
                }

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    fun updateRequirement(fieldName: String, newValue: Int) {
        val currentTrial = createdTrial ?: return
        val req = currentTrial.requirements

        val updatedReq = when (fieldName) {
            "acceleration" -> req.copy(acceleration = newValue)
            "sprint_speed" -> req.copy(sprint_speed = newValue)
            "finishing" -> req.copy(finishing = newValue)
            "shot_power" -> req.copy(shot_power = newValue)
            "long_shots" -> req.copy(long_shots = newValue)
            "penalties" -> req.copy(penalties = newValue)
            "short_pass" -> req.copy(short_pass = newValue)
            "long_pass" -> req.copy(long_pass = newValue)
            "agility" -> req.copy(agility = newValue)
            "balance" -> req.copy(balance = newValue)
            "ball_control" -> req.copy(ball_control = newValue)
            "dribbling" -> req.copy(dribbling = newValue)
            "heading_acc" -> req.copy(heading_acc = newValue)
            "jumping" -> req.copy(jumping = newValue)
            "stamina" -> req.copy(stamina = newValue)
            "strength" -> req.copy(strength = newValue)
            else -> req
        }

        createdTrial = currentTrial.copy(requirements = updatedReq)
    }


}

