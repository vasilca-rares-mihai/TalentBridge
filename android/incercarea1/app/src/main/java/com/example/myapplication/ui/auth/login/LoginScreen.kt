package com.example.myapplication.ui.auth.login

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.AlertDialogDefaults.containerColor
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.myapplication.data.model.AccountType
import com.example.myapplication.ui.auth.login.LoginViewModel
import com.example.myapplication.ui.auth.createAccount.CreateAccountScreen
import com.example.myapplication.ui.auth.createAccount.CreateAccountViewModel
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor

@Composable
fun LoginScreen(loginViewModel: LoginViewModel = viewModel(), onLoginSuccess: (String) -> Unit, onCreateAccountclick: (AccountType) -> Unit) {

    var displayCreateAccount by remember { mutableStateOf(false) }

    if (loginViewModel.loginSuccessToken != null) {
        onLoginSuccess(loginViewModel.loginSuccessToken!!)
        loginViewModel.loginSuccessToken = null
    }

    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(vertical = 60.dp, horizontal = 16.dp).fillMaxWidth()) {

            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(2.dp),
                colors = CardDefaults.cardColors(containerColor = card_color)
            ) {
                Column(
                    modifier = Modifier.padding(20.dp).verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {

                    Text(
                        text = "Login",
                        style = MaterialTheme.typography.headlineSmall,
                        fontFamily = FontFamily.SansSerif,
                        fontWeight = FontWeight.ExtraBold,
                    )
                    OutlinedTextField(
                        value = loginViewModel.email,
                        //value = "chelsea@test.ro",
                        onValueChange = { loginViewModel.email = it },
                        label = { Text("Email") },
                        textStyle = TextStyle(color = fontTextColor),
                        modifier = Modifier.fillMaxWidth()
                    )

                    OutlinedTextField(
                        value = loginViewModel.password,
                        //value = "chelsea",
                        onValueChange = { loginViewModel.password = it },
                        visualTransformation = PasswordVisualTransformation(),
                        label = { Text("Password") },
                        textStyle = TextStyle(color = fontTextColor),
                        modifier = Modifier.fillMaxWidth()
                    )

                    Button(
                        onClick = { loginViewModel.performLogin() },
                        modifier = Modifier.fillMaxWidth().padding(top = 8.dp).height(50.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                            contentColor = button_text_color)
                    ) {
                        Text("Login", style = MaterialTheme.typography.titleMedium)
                    }

                    Button(
                        onClick = { displayCreateAccount = true },
                        modifier = Modifier.fillMaxWidth().padding(top = 8.dp).height(50.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                            contentColor = button_text_color)
                    ) {
                        Text("Create Account", style = MaterialTheme.typography.titleMedium)
                    }
                    if (displayCreateAccount) {
                        AlertDialog(
                            onDismissRequest = { displayCreateAccount = true },
                            title = { Text("Create a new account") },
                            text = {
                                Column(modifier = Modifier.fillMaxWidth()) {
                                    Button(
                                        onClick = { onCreateAccountclick(AccountType.athlete) },
                                        modifier = Modifier.fillMaxWidth(),
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                            contentColor = button_text_color)
                                    ) {
                                        Text(
                                            "Athlete account"
                                        )
                                    }
                                    Button(
                                        onClick = { onCreateAccountclick(AccountType.football_club) },
                                        modifier = Modifier.fillMaxWidth(),
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                            contentColor = button_text_color)
                                    ) {
                                        Text(
                                            "Football club account"
                                        )
                                    }
                                }
                            },
                            confirmButton = {},
                            dismissButton = {
                                Button(
                                    onClick = {
                                        displayCreateAccount = false
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                        contentColor = button_text_color)
                                ) { Text("Back") }
                            }
                        )
                    }
                }
            }
        }
    }

}