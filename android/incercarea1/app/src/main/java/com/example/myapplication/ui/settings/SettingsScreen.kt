package com.example.myapplication.ui.settings

import DatePickerField
import EnumDropdownField
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.FieldPositionsEnum
import com.example.myapplication.data.model.WeakFootEnum
import com.example.myapplication.data.network.RetrofitClient
import com.example.myapplication.ui.getRoleFromToken
import com.example.myapplication.ui.profile.ProfileViewModel
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_red_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor


@Composable
fun SettingsScreen(settingsViewModel: SettingsViewModel, token: String, profileViewModel : ProfileViewModel, onLogout: () -> Unit, modifier: Modifier = Modifier) {

    var displayChangeEmail by remember { mutableStateOf(false) }
    var displayChangePassword by remember { mutableStateOf(false) }
    var displayChangeAthleteInfo by remember { mutableStateOf(false) }
    var displayDeleteAccount by remember { mutableStateOf(false) }
    val role = getRoleFromToken(token)

    if (settingsViewModel.updateSuccess) {
        settingsViewModel.updateSuccess = false
        onLogout()
    }

    LaunchedEffect(profileViewModel.email) {
        if (settingsViewModel.email.isBlank() && profileViewModel.email != "") {
            settingsViewModel.email = profileViewModel.email
        }
    }
    LaunchedEffect(displayChangeAthleteInfo) {
        if (displayChangeAthleteInfo) {
            settingsViewModel.dataToupdate(token, profileViewModel.athlete)
        }
    }
    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(vertical = 60.dp, horizontal = 16.dp).fillMaxWidth()) {

            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(modifier = Modifier.padding(20.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {

                    Text(
                        text = "Settings",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor,
                    )
                    Spacer(modifier = Modifier.height(5.dp))
                    //email

                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {

                        Button(
                            onClick = { displayChangeEmail = true },
                            modifier = Modifier.fillMaxWidth().height(50.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                contentColor = button_text_color)
                        ) {
                            Text(text = "Change Email")
                        }

                        if (displayChangeEmail) {
                            AlertDialog(
                                onDismissRequest = { displayChangeEmail = false },
                                title = { Text("Change email") },
                                text = {
                                    Column {
                                        TextField(
                                            value = settingsViewModel.changeEmailData.email,
                                            onValueChange = {
                                                settingsViewModel.changeEmailData =
                                                    settingsViewModel.changeEmailData.copy(email = it)
                                            },
                                            label = { Text("New email") }
                                        )


                                        TextField(
                                            value = settingsViewModel.changeEmailData.password,
                                            onValueChange = {
                                                settingsViewModel.changeEmailData =
                                                    settingsViewModel.changeEmailData.copy(password = it)
                                            },
                                            label = { Text("Your password") }
                                        )

                                    }
                                },
                                confirmButton = {
                                    Button(
                                        onClick = {
                                            settingsViewModel.update_email(
                                                token,
                                                settingsViewModel.changeEmailData
                                            ); displayChangeEmail = false
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                            contentColor = button_text_color)
                                    ) { Text("Save") }
                                },
                                dismissButton = {
                                    Button(
                                        onClick = { displayChangeEmail = false },
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                            contentColor = button_text_color)
                                    ) { Text("Back") }
                                })

                        }


                        //password
                        Button(
                            onClick = { displayChangePassword = true },
                            modifier = Modifier.fillMaxWidth().height(50.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                contentColor = button_text_color)
                        ) {
                            Text("Update password")
                        }
                        if (displayChangePassword) {
                            AlertDialog(
                                onDismissRequest = { displayChangePassword = true },
                                title = { Text("Change password") },
                                text = {
                                    Column {
                                        TextField(
                                            value = settingsViewModel.updated_password.old_password,
                                            onValueChange = {
                                                settingsViewModel.updated_password =
                                                    settingsViewModel.updated_password.copy(
                                                        old_password = it
                                                    )
                                            },
                                            label = { Text("old password") }
                                        )
                                        TextField(
                                            value = settingsViewModel.updated_password.new_password,
                                            onValueChange = {
                                                settingsViewModel.updated_password =
                                                    settingsViewModel.updated_password.copy(
                                                        new_password = it
                                                    )
                                            },
                                            label = { Text("new password") }
                                        )
                                        TextField(
                                            value = settingsViewModel.updated_password.new_password_confirm,
                                            onValueChange = {
                                                settingsViewModel.updated_password =
                                                    settingsViewModel.updated_password.copy(
                                                        new_password_confirm = it
                                                    )
                                            },
                                            label = { Text("new password confirmed") }
                                        )
                                    }
                                },
                                confirmButton = {
                                    Button(
                                        onClick = {
                                            settingsViewModel.update_password(
                                                token,
                                                settingsViewModel.updated_password
                                            )
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                            contentColor = button_text_color)
                                    ) { Text("Save") }
                                },
                                dismissButton = {
                                    Button(
                                        onClick = { displayChangePassword = false },
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                            contentColor = button_text_color)
                                    ) { Text("Back") }
                                }
                            )
                        }

                        if (role == "athlete") {
                            //athlete info
                            Button(
                                onClick = { displayChangeAthleteInfo = true },
                                modifier = Modifier.fillMaxWidth().height(50.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = button_color,
                                    contentColor = button_text_color
                                )
                            ) {
                                Text("Update athlete's info")
                            }

                            if (displayChangeAthleteInfo && settingsViewModel.athlete != null) {
                                AlertDialog(
                                    onDismissRequest = { displayChangeAthleteInfo = false },
                                    title = { Text("Update info") },
                                    text = {
                                        Column {
                                            OutlinedTextField(
                                                value = settingsViewModel.athlete?.first_name ?: "",
                                                onValueChange = { newValue ->
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete?.copy(first_name = newValue)
                                                },
                                                label = { Text("First name") }
                                            )

                                            OutlinedTextField(
                                                value = settingsViewModel.athlete?.second_name
                                                    ?: "",
                                                onValueChange = { newValue ->
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete?.copy(second_name = newValue)
                                                },
                                                label = { Text("Second name") }
                                            )

                                            EnumDropdownField(
                                                label = "Field position",
                                                currentValue = settingsViewModel.athlete!!.field_position,
                                                options = FieldPositionsEnum.entries.map { it.name },
                                                onSelectionChanged = { nouaPozitie ->
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete!!.copy(
                                                            field_position = nouaPozitie
                                                        )
                                                }
                                            )
                                            EnumDropdownField(
                                                label = "Weak foot",
                                                currentValue = settingsViewModel.athlete!!.weak_foot,
                                                options = WeakFootEnum.entries.map { it.name },
                                                onSelectionChanged = { piciorNou ->
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete!!.copy(weak_foot = piciorNou)
                                                }
                                            )
                                            Row(
                                                modifier = Modifier.fillMaxWidth(),
                                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                                            ) {
                                                OutlinedTextField(
                                                    value = settingsViewModel.athlete!!.height.toString(),
                                                    onValueChange = {
                                                        settingsViewModel.athlete =
                                                            settingsViewModel.athlete!!.copy(
                                                                height = it.toFloatOrNull() ?: 0f
                                                            )
                                                    },
                                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                                    label = { Text("Height (m)") },
                                                    modifier = Modifier.weight(1f)
                                                )

                                                OutlinedTextField(
                                                    value = settingsViewModel.athlete!!.weight.toString(),
                                                    onValueChange = {
                                                        settingsViewModel.athlete =
                                                            settingsViewModel.athlete!!.copy(
                                                                weight = it.toFloatOrNull() ?: 0f
                                                            )
                                                    },
                                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                                    label = { Text("Weight (kg)") },
                                                    modifier = Modifier.weight(1f)
                                                )
                                            }
                                            OutlinedTextField(
                                                value = settingsViewModel.athlete!!.country,
                                                onValueChange = {
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete!!.copy(country = it)
                                                },
                                                label = { Text("Country") },
                                                modifier = Modifier.fillMaxWidth()
                                            )

                                            OutlinedTextField(
                                                value = settingsViewModel.athlete!!.region,
                                                onValueChange = {
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete!!.copy(region = it)
                                                },
                                                label = { Text("Region") },
                                                modifier = Modifier.fillMaxWidth()
                                            )

                                            OutlinedTextField(
                                                value = settingsViewModel.athlete!!.city,
                                                onValueChange = {
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete!!.copy(city = it)
                                                },
                                                label = { Text("City") },
                                                modifier = Modifier.fillMaxWidth()
                                            )

                                            OutlinedTextField(
                                                value = settingsViewModel.athlete!!.phone_number,
                                                onValueChange = {
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete!!.copy(
                                                            phone_number = it
                                                        )
                                                },
                                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                                                label = { Text("Phone number") },
                                                modifier = Modifier.fillMaxWidth()
                                            )

                                            DatePickerField(
                                                label = "Date of birth",
                                                currentDate = settingsViewModel.athlete!!.date_of_birth,
                                                onDateSelected = { newDate ->
                                                    settingsViewModel.athlete =
                                                        settingsViewModel.athlete!!.copy(
                                                            date_of_birth = newDate
                                                        )
                                                }
                                            )


                                        }
                                    },
                                    confirmButton = {
                                        Button(
                                            onClick = {
                                                settingsViewModel.update_athlete_info(token,settingsViewModel.athlete!!)
                                                displayChangeAthleteInfo = false
                                            },
                                            colors = ButtonDefaults.buttonColors(
                                                containerColor = button_color,
                                                contentColor = button_text_color
                                            )
                                        ) {
                                            Text("Save")
                                        }
                                    },
                                    dismissButton = {
                                        Button(
                                            onClick = { displayChangeAthleteInfo = false },
                                            colors = ButtonDefaults.buttonColors(
                                                containerColor = button_color,
                                                contentColor = button_text_color
                                            )
                                        ) {
                                            Text("Back")
                                        }
                                    }
                                )

                            }
                        } else if (role == "football_club") {
                            Button(
                                onClick = { displayChangeAthleteInfo = true },
                                modifier = Modifier.fillMaxWidth().height(50.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = button_color,
                                    contentColor = button_text_color
                                )
                            ) {
                                Text("Update football club's info")
                            }

                            if (displayChangeAthleteInfo) {
                                settingsViewModel.football_club = settingsViewModel.football_club ?: profileViewModel.football_club
                                AlertDialog(
                                    onDismissRequest = { displayChangeAthleteInfo = false },
                                    title = { Text("Update info") },
                                    text = {
                                        Column {
                                            OutlinedTextField(
                                                value = settingsViewModel.football_club?.name ?: "",
                                                onValueChange = { newValue ->
                                                    settingsViewModel.football_club =
                                                        settingsViewModel.football_club?.copy(name = newValue)
                                                },
                                                label = { Text("Name") }
                                            )

                                            OutlinedTextField(
                                                value = settingsViewModel.football_club?.country
                                                    ?: "",
                                                onValueChange = { newValue ->
                                                    settingsViewModel.football_club =
                                                        settingsViewModel.football_club?.copy(country = newValue)
                                                },
                                                label = { Text("Country") }
                                            )
                                            OutlinedTextField(
                                                value = settingsViewModel.football_club?.info
                                                    ?: "",
                                                onValueChange = { newValue ->
                                                    settingsViewModel.football_club =
                                                        settingsViewModel.football_club?.copy(info = newValue)
                                                },
                                                label = { Text("Info") }
                                            )
                                        }
                                    },
                                    confirmButton = {
                                        Button(
                                            onClick = {
                                                settingsViewModel.update_fc_info(token,settingsViewModel.football_club!!)
                                                displayChangeAthleteInfo = false
                                            },
                                            colors = ButtonDefaults.buttonColors(
                                                containerColor = button_color,
                                                contentColor = button_text_color
                                            )
                                        ) {
                                            Text("Save")
                                        }
                                    },
                                    dismissButton = {
                                        Button(
                                            onClick = { displayChangeAthleteInfo = false },
                                            colors = ButtonDefaults.buttonColors(
                                                containerColor = button_color,
                                                contentColor = button_text_color
                                            )
                                        ) {
                                            Text("Back")
                                        }
                                    }
                                )

                            }
                        }

                        //delete account
                        Button(
                            onClick = { displayDeleteAccount = true },
                            modifier = Modifier.fillMaxWidth().height(50.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = button_red_color,
                                contentColor = button_text_color)
                        ) {
                            Text("Delete account")
                        }
                        if (displayDeleteAccount) {
                            AlertDialog(
                                onDismissRequest = { displayDeleteAccount = false },
                                title = { Text("Are you sure you want to delete your account?") },
                                confirmButton = {
                                    Button(onClick = { settingsViewModel.delete_athlete(token) },
                                        colors = ButtonDefaults.buttonColors(containerColor = button_red_color,
                                        contentColor = button_text_color)) {
                                        Text("Yes")} },
                                dismissButton = {
                                    Button(onClick = { displayDeleteAccount = false },
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                        contentColor = button_text_color)) { Text("Back") }
                                }
                            )

                        }

                    }
                }
            }
        }
    }
}
