package com.example.myapplication.ui.fc_search_athlete

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
import androidx.compose.foundation.layout.width
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
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color.Companion.Red
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.FieldPositionsEnum
import com.example.myapplication.data.model.GenderEnum
import com.example.myapplication.data.model.WeakFootEnum
import com.example.myapplication.ui.profile.AttributeStat
import com.example.myapplication.ui.profile.ProfileInfoRow
import com.example.myapplication.ui.theme.Green
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_red_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import com.example.myapplication.ui.watchlist.WatchlistViewModel
import java.text.SimpleDateFormat
import java.util.Locale

@Composable
fun SearchAdminScreen(token: String, searchFCViewModel: SearchViewModel, modifier: Modifier = Modifier) {

    var displaySearchedAthletes by remember { mutableStateOf(false) }
    var displaySearchedFC by remember { mutableStateOf(false) }
    var displayDeleteA by remember { mutableStateOf(false)}
    var displayDeleteFC by remember { mutableStateOf(false)}

    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 60.dp).fillMaxWidth().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column( modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Search athletes",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    Column(modifier = Modifier.fillMaxWidth().padding(16.dp),verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        OutlinedTextField(
                            value = searchFCViewModel.athleteFilters.first_name,
                            onValueChange = { searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(first_name = it) },
                            label = { Text("First name") },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            textStyle = TextStyle(color = fontTextColor),
                            singleLine = true
                        )

                        OutlinedTextField(
                            value = searchFCViewModel.athleteFilters.second_name,
                            onValueChange = { searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(second_name = it) },
                            label = { Text("Second name") },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            textStyle = TextStyle(color = fontTextColor),
                            singleLine = true
                        )

                        OutlinedTextField(
                            value = searchFCViewModel.athleteFilters.country,
                            onValueChange = { searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(country = it) },
                            label = { Text("Country") },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            textStyle = TextStyle(color = fontTextColor),
                            singleLine = true
                        )


                        Box(modifier = Modifier.fillMaxWidth().height(56.dp)) {
                            EnumDropdownField(
                                label = "Field position",
                                currentValue = searchFCViewModel.athleteFilters.field_position,
                                options = FieldPositionsEnum.entries.map { it.name },
                                onSelectionChanged = { searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(field_position = it.lowercase()) }
                            )
                        }

                        Box(modifier = Modifier.fillMaxWidth().height(56.dp)) {
                            EnumDropdownField(
                                label = "Weak foot",
                                currentValue = searchFCViewModel.athleteFilters.weak_foot,
                                options = WeakFootEnum.entries.map { it.name },
                                onSelectionChanged = { searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(weak_foot = it.lowercase()) }
                            )
                        }
                        Box(modifier = Modifier.fillMaxWidth().height(56.dp)) {
                            EnumDropdownField(
                                label = "Gender",
                                currentValue = searchFCViewModel.athleteFilters.gender,
                                options = GenderEnum.entries.map { it.name },
                                onSelectionChanged = {
                                    val formattedGender = it.lowercase().replaceFirstChar { char -> char.uppercase() }
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(gender = formattedGender)
                                }
                            )
                        }

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.age_range?.get(0)?.toString() ?: "",
                                onValueChange = {
                                    val newVal = it.toIntOrNull()
                                    val currentList = searchFCViewModel.athleteFilters.age_range ?: listOf(null, null)
                                    val newList = listOf(newVal, currentList[1])
                                    val finalRange = if (newList[0] == null && newList[1] == null) null else newList
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(age_range = finalRange)
                                },
                                label = { Text("Min Age") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.age_range?.get(1)?.toString() ?: "",
                                onValueChange = {
                                    val newVal = it.toIntOrNull()
                                    val currentList = searchFCViewModel.athleteFilters.age_range ?: listOf(null, null)
                                    val newList = listOf(currentList[0], newVal)

                                    val finalRange = if (newList[0] == null && newList[1] == null) null else newList
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(age_range = finalRange)
                                },
                                label = { Text("Max Age") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                        }

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.height_range?.get(0)?.toString()?:"",
                                onValueChange = { val newVal = it.toFloatOrNull() ?: 0f; searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(height_range = listOf(newVal,
                                    searchFCViewModel.athleteFilters.height_range?.get(1)
                                )) },
                                label = { Text("Min Height (m)") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.height_range?.get(1)?.toString()?:"",
                                onValueChange = { val newVal = it.toFloatOrNull() ?: 250f; searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(height_range = listOf(
                                    searchFCViewModel.athleteFilters.height_range?.get(0), newVal)) },
                                label = { Text("Max Height (m)") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                        }

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.weight_range?.get(0)?.toString()?:"",
                                onValueChange = { val newVal = it.toFloatOrNull() ?: 0f; searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(weight_range = listOf(newVal,
                                    searchFCViewModel.athleteFilters.weight_range?.get(1)
                                )) },
                                label = { Text("Min Weight (kg)") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.weight_range?.get(1)?.toString()?:"",
                                onValueChange = { val newVal = it.toFloatOrNull() ?: 150f; searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(weight_range = listOf(
                                    searchFCViewModel.athleteFilters.weight_range?.get(0), newVal)) },
                                label = { Text("Max Weight (kg)") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        Button(
                            onClick = {
                                searchFCViewModel.performAthleteSearch(token)
                                displaySearchedAthletes = true
                            },
                            modifier = Modifier.height(50.dp).fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                contentColor = button_text_color)
                        ) {Text("Search Athletes", fontWeight = FontWeight.Bold)}
                    }

                }

            }

            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column( modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Search football clubs",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    Column(modifier = Modifier.fillMaxWidth().padding(16.dp),verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        OutlinedTextField(
                            value = searchFCViewModel.fcFilters.name,
                            onValueChange = { searchFCViewModel.fcFilters = searchFCViewModel.fcFilters.copy(name = it) },
                            label = { Text("Name") },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            textStyle = TextStyle(color = fontTextColor),
                            singleLine = true
                        )

                        OutlinedTextField(
                            value = searchFCViewModel.fcFilters.country,
                            onValueChange = { searchFCViewModel.fcFilters = searchFCViewModel.fcFilters.copy(country = it) },
                            label = { Text("Country") },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            textStyle = TextStyle(color = fontTextColor),
                            singleLine = true
                        )
                        Button(
                            onClick = {
                                searchFCViewModel.performFCSearch(token)
                                displaySearchedFC = true
                            },
                            modifier = Modifier.height(50.dp).fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                contentColor = button_text_color)
                        ) {Text("Search football clubs", fontWeight = FontWeight.Bold)}

                    }

                }

            }

        }
    }
    if (displaySearchedAthletes) {
        AlertDialog(
            onDismissRequest = { displaySearchedAthletes = false },
            title = { Text("Searched athletes") },
            text = {
                Column(modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState()),verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    for (athlete in searchFCViewModel.athletes) {
                        if (athlete != null) {

                                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), horizontalArrangement = Arrangement.SpaceBetween ) {

                                    Text(
                                        text = "${athlete.first_name} ${athlete.second_name}",
                                        color = fontTextColor,
                                        fontWeight = FontWeight.Bold
                                    )

                                    Button(onClick = {  displayDeleteA= true},
                                        colors = ButtonDefaults.buttonColors(containerColor = button_red_color,
                                            contentColor = button_text_color)
                                    ) {
                                        Text("Delete")
                                    }
                                }
                            }

                    }
                }

            },
            confirmButton = {},
            dismissButton = {
                Button(
                    onClick = { displaySearchedAthletes = false },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = button_color,
                        contentColor = button_text_color
                    )
                ) { Text("Back")}
            }
        )
    }

    if (displaySearchedFC) {
        AlertDialog(
            onDismissRequest = { displaySearchedFC = false },
            title = { Text("Searched FC") },
            text = {
                Column(modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState()),verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    for (fc in searchFCViewModel.football_clubs) {
                        if (fc != null) {

                                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), horizontalArrangement = Arrangement.SpaceBetween ) {

                                    Text(
                                        text = "${fc.name} ${fc.country}",
                                        color = fontTextColor,
                                        fontWeight = FontWeight.Bold
                                    )

                                    Button(onClick = {  displayDeleteFC= true},
                                        colors = ButtonDefaults.buttonColors(containerColor = button_red_color,
                                            contentColor = button_text_color)
                                    ) {
                                        Text("Delete")
                                    }
                                }

                        }
                    }
                }

            },
            confirmButton = {},
            dismissButton = {
                Button(
                    onClick = { displaySearchedFC = false },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = button_color,
                        contentColor = button_text_color
                    )
                ) { Text("Back")}
            }
        )
    }
    if (displayDeleteA == true) {
        AlertDialog(
            onDismissRequest = { displayDeleteA = false },
            title = { Text("Are you sure you want to delete this athlete?") },
            text = {},
            confirmButton = {
                Button(
                    onClick = { ;
                        displayDeleteA = false
                              searchFCViewModel.delete_user(token, searchFCViewModel.athletes[0].user_id, true)
                              },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = button_red_color,
                        contentColor = button_text_color
                    )
                ) { Text("Yes") }},
            dismissButton = {
                Button(
                    onClick = { displayDeleteA = false},
                    colors = ButtonDefaults.buttonColors(
                        containerColor = button_color,
                        contentColor = button_text_color
                    )
                ) { Text("Back") }
            }
        )
    }

    if (displayDeleteFC == true) {
        AlertDialog(
            onDismissRequest = { displayDeleteFC = false },
            title = { Text("Are you sure you want to delete this football club?") },
            text = {},
            confirmButton = {
                Button(
                    onClick = { ;
                        displayDeleteFC = false
                        searchFCViewModel.delete_user(token, searchFCViewModel.football_clubs[0].user_id, false)
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = button_red_color,
                        contentColor = button_text_color
                    )
                ) { Text("Yes") }},
            dismissButton = {
                Button(
                    onClick = { displayDeleteFC = false},
                    colors = ButtonDefaults.buttonColors(
                        containerColor = button_color,
                        contentColor = button_text_color
                    )
                ) { Text("Back") }
            }
        )
    }
    LaunchedEffect(Unit) {
    }
}