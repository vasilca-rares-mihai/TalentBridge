package com.example.myapplication.ui.auth.login

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.network.RetrofitClient
import kotlinx.coroutines.launch

class LoginViewModel : ViewModel() {
    var email by mutableStateOf("")
    var password by mutableStateOf("")

    var isLoading by mutableStateOf(false)
    var errorMessage by mutableStateOf<String?>(null)
    var loginSuccessToken by mutableStateOf<String?>(null)


    fun performLogin() {
        if(email.isBlank() || password.isBlank()) {
            errorMessage = "Uncompleted fields"
            return
        }
        isLoading = true
        errorMessage = null

        viewModelScope.launch {
            try {
                val loginResponse = RetrofitClient.authApi.login(email, password)
                loginSuccessToken = loginResponse.access_token
                isLoading = false


            } catch (e: Exception){
                isLoading = false
                errorMessage = "Auth error: ${e.localizedMessage}"
            }

        }

    }

}