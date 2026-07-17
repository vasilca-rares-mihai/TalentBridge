package com.example.myapplication.ui.auth.createAccount

import DatePickerField
import EnumDropdownField
import android.R.attr.text
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.myapplication.data.model.AccountType
import com.example.myapplication.data.model.FieldPositionsEnum
import com.example.myapplication.data.model.GenderEnum
import com.example.myapplication.data.model.WeakFootEnum
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import java.util.Date

@Composable
fun CreateAccountScreen(createAccountViewModel: CreateAccountViewModel = viewModel(), selectedAccountType: AccountType, onAccountCreated: (String) -> Unit, onNavigateBack: () -> Unit) {

    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(vertical = 60.dp, horizontal = 16.dp).fillMaxWidth()) {

            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(
                    modifier = Modifier.padding(20.dp).verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "Personal Info",
                        style = MaterialTheme.typography.headlineSmall,
                        fontFamily = FontFamily.SansSerif,
                        fontWeight = FontWeight.ExtraBold
                    )

                    OutlinedTextField(
                        value = createAccountViewModel.email,
                        onValueChange = { createAccountViewModel.email = it },
                        label = { Text("Email") },
                        textStyle = TextStyle(color = fontTextColor),
                        modifier = Modifier.fillMaxWidth()
                    )

                    OutlinedTextField(
                        value = createAccountViewModel.password,
                        onValueChange = { createAccountViewModel.password = it },
                        visualTransformation = PasswordVisualTransformation(),
                        label = { Text("Password") },
                        textStyle = TextStyle(color = fontTextColor),
                        modifier = Modifier.fillMaxWidth()
                    )

                    if (selectedAccountType == AccountType.athlete && createAccountViewModel.athleteInfo != null) {
                        OutlinedTextField(
                            value = createAccountViewModel.athleteInfo!!.first_name,
                            onValueChange = {
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(first_name = it)
                            },
                            label = { Text("First name") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = createAccountViewModel.athleteInfo!!.second_name,
                            onValueChange = {
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(second_name = it)
                            },
                            label = { Text("Second name") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = createAccountViewModel.athleteInfo!!.age.toString(),
                            onValueChange = {
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(
                                        age = it.toIntOrNull() ?: 0
                                    )
                            },
                            label = { Text("Age") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth(),
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                        )

                        EnumDropdownField(
                            label = "Field position",
                            currentValue = createAccountViewModel.athleteInfo!!.field_position,
                            options = FieldPositionsEnum.entries.map { it.name },
                            onSelectionChanged = { nouaPozitie ->
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(field_position = nouaPozitie)
                            }
                        )

                        EnumDropdownField(
                            label = "Weak foot",
                            currentValue = createAccountViewModel.athleteInfo!!.weak_foot,
                            options = WeakFootEnum.entries.map { it.name },
                            onSelectionChanged = { piciorNou ->
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(weak_foot = piciorNou)
                            }
                        )

                        EnumDropdownField(
                            label = "Gender",
                            currentValue = createAccountViewModel.athleteInfo!!.gender,
                            options = GenderEnum.entries.map { it.name },
                            onSelectionChanged = { genderNou ->
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(gender = genderNou)
                            }
                        )

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp) ) {
                            OutlinedTextField(
                                value = createAccountViewModel.athleteInfo!!.height.toString(),
                                onValueChange = {
                                    createAccountViewModel.athleteInfo =
                                        createAccountViewModel.athleteInfo!!.copy(
                                            height = it.toFloatOrNull() ?: 0f
                                        )
                                },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                label = { Text("Height (m)") },
                                textStyle = TextStyle(color = fontTextColor),
                                modifier = Modifier.weight(1f)
                            )

                            OutlinedTextField(
                                value = createAccountViewModel.athleteInfo!!.weight.toString(),
                                onValueChange = {
                                    createAccountViewModel.athleteInfo =
                                        createAccountViewModel.athleteInfo!!.copy(
                                            weight = it.toFloatOrNull() ?: 0f
                                        )
                                },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                label = { Text("Weight (kg)") },
                                textStyle = TextStyle(color = fontTextColor),
                                modifier = Modifier.weight(1f)
                            )
                        }

                        OutlinedTextField(
                            value = createAccountViewModel.athleteInfo!!.country,
                            onValueChange = {
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(country = it)
                            },
                            label = { Text("Country") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = createAccountViewModel.athleteInfo!!.region,
                            onValueChange = {
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(region = it)
                            },
                            label = { Text("Region") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = createAccountViewModel.athleteInfo!!.city,
                            onValueChange = {
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(city = it)
                            },
                            label = { Text("City") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = createAccountViewModel.athleteInfo!!.phone_number,
                            onValueChange = {
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(phone_number = it)
                            },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                            label = { Text("Phone number") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        DatePickerField(
                            label = "Date of birth",
                            currentDate = createAccountViewModel.athleteInfo!!.date_of_birth,
                            onDateSelected = { newDate ->
                                createAccountViewModel.athleteInfo =
                                    createAccountViewModel.athleteInfo!!.copy(date_of_birth = newDate)
                            }
                        )
                    } else if (selectedAccountType == AccountType.football_club && createAccountViewModel.football_clubInfo != null) {
                        OutlinedTextField(
                            value = createAccountViewModel.football_clubInfo!!.name,
                            onValueChange = {
                                createAccountViewModel.football_clubInfo =
                                    createAccountViewModel.football_clubInfo!!.copy(name = it)
                            },
                            label = { Text("Nume") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = createAccountViewModel.football_clubInfo!!.country,
                            onValueChange = {
                                createAccountViewModel.football_clubInfo =
                                    createAccountViewModel.football_clubInfo!!.copy(country = it)
                            },
                            label = { Text("Country") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = createAccountViewModel.football_clubInfo!!.info
                                ?: "",
                            onValueChange = { newValue ->
                                createAccountViewModel.football_clubInfo =
                                    createAccountViewModel.football_clubInfo!!.copy(info = newValue)
                            },
                            label = { Text("Info") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    createAccountViewModel.errorMessage?.let { mesajEroare ->
                        Text(
                            text = mesajEroare,
                            color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    }

                    Button(
                        onClick = {
                            createAccountViewModel.createAccount(
                                selectedAccountType,
                                onSuccess = { onNavigateBack() })
                        },
                        modifier = Modifier.fillMaxWidth().padding(top = 8.dp).height(50.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                            contentColor = button_text_color)
                    ) {
                        Text("Create account", style = MaterialTheme.typography.titleMedium)
                    }

                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
        }
    }
}