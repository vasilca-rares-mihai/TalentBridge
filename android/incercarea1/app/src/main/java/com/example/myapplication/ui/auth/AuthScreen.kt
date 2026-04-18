package com.example.myapplication.ui.auth

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.myapplication.data.model.AccountType
import com.example.myapplication.ui.auth.createAccount.CreateAccountScreen
import com.example.myapplication.ui.auth.createAccount.CreateAccountViewModel
import com.example.myapplication.ui.auth.login.LoginScreen
import com.example.myapplication.ui.auth.login.LoginViewModel

@Composable
fun AuthScreen(createAccountViewModel: CreateAccountViewModel = viewModel(), loginViewModel: LoginViewModel = viewModel(), onLoginSuccess: (String) -> Unit, onAccountCreated: (String) -> Unit) {
    val navController = rememberNavController()
    var selectedAccountType by remember { mutableStateOf<AccountType?>(null) }

    NavHost(navController = navController, startDestination = "login") {
        composable("login") {
            LoginScreen(
                loginViewModel = loginViewModel,
                onCreateAccountclick = { type ->
                    selectedAccountType = type
                    navController.navigate("create_athlete") },
                onLoginSuccess = onLoginSuccess
            )
        }

        composable("create_athlete") {
            CreateAccountScreen(
                createAccountViewModel = createAccountViewModel,
                selectedAccountType = selectedAccountType!!,
                onAccountCreated = onAccountCreated,
                onNavigateBack = { navController.popBackStack() }
            )
        }

    }
}