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
import com.example.myapplication.data.model.WeakFootEnum
import com.example.myapplication.ui.profile.AttributeStat
import com.example.myapplication.ui.profile.ProfileInfoRow
import com.example.myapplication.ui.theme.Green
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import com.example.myapplication.ui.watchlist.WatchlistViewModel
import java.text.SimpleDateFormat
import java.util.Locale

@Composable
fun SearchFootballClubScreen(token: String, searchFCViewModel: SearchViewModel, watchlistViewModel: WatchlistViewModel, modifier: Modifier = Modifier) {

    var displaySearchedAthletes by remember { mutableStateOf(false) }
    var displayCompareAthletes by remember { mutableStateOf(false) }
    var athleteToShowInfo by remember { mutableStateOf<AthleteData?>(null) }
    var athleteToShowAttributes by remember { mutableStateOf<AthleteData?>(null) }

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

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.age_range?.get(0)?.toString() ?: "",
                                onValueChange = {
                                    val newVal = it.toIntOrNull()
                                    val currentList = searchFCViewModel.athleteFilters.age_range ?: listOf(null, null)
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(age_range = listOf(newVal, currentList[1]))
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
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(age_range = listOf(currentList[0], newVal))
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
                                value = searchFCViewModel.athleteFilters.height_range?.get(0)?.toString() ?: "",
                                onValueChange = {
                                    val newVal = it.toFloatOrNull()
                                    val currentList = searchFCViewModel.athleteFilters.height_range ?: listOf(null, null)
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(height_range = listOf(newVal, currentList[1]))
                                },
                                label = { Text("Min Height (cm)") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.height_range?.get(1)?.toString() ?: "",
                                onValueChange = {
                                    val newVal = it.toFloatOrNull()
                                    val currentList = searchFCViewModel.athleteFilters.height_range ?: listOf(null, null)
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(height_range = listOf(currentList[0], newVal))
                                },
                                label = { Text("Max Height (cm)") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                        }

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.weight_range?.get(0)?.toString() ?: "",
                                onValueChange = {
                                    val newVal = it.toFloatOrNull()
                                    val currentList = searchFCViewModel.athleteFilters.weight_range ?: listOf(null, null)
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(weight_range = listOf(newVal, currentList[1]))
                                },
                                label = { Text("Min Weight (kg)") },
                                modifier = Modifier.weight(1f).height(56.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                            OutlinedTextField(
                                value = searchFCViewModel.athleteFilters.weight_range?.get(1)?.toString() ?: "",
                                onValueChange = {
                                    val newVal = it.toFloatOrNull()
                                    val currentList = searchFCViewModel.athleteFilters.weight_range ?: listOf(null, null)
                                    searchFCViewModel.athleteFilters = searchFCViewModel.athleteFilters.copy(weight_range = listOf(currentList[0], newVal))
                                },
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
                        text = "Compare athletes",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    for (i in 0 until watchlistViewModel.athletesWatchlist.size) {
                        val athlete = watchlistViewModel.athletesWatchlist[i]
                        Column(modifier = Modifier.padding(8.dp)) {
                            Row(modifier = Modifier.fillMaxWidth()) {
                                Text(
                                    text = "${athlete.first_name} ${athlete.second_name}",
                                    color = fontTextColor,
                                    fontWeight = FontWeight.Bold
                                )

                                Spacer(modifier = Modifier.weight(1f))
                                if (athlete !in searchFCViewModel.compareList) {
                                    Button(
                                        onClick = {searchFCViewModel.addToCOmapre(athlete)},
                                        modifier = Modifier.height(50.dp).width(100.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                            contentColor = button_text_color)
                                    ) {Text("ADD CL", fontWeight = FontWeight.Bold)}
                                } else {
                                    Button(
                                        onClick = {searchFCViewModel.rmFromComapre(athlete)},
                                        modifier = Modifier.height(50.dp).width(100.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = Green,
                                            contentColor = button_text_color)
                                    ) {Text("ADDED", fontWeight = FontWeight.Bold)}
                                }
                            }
                        }
                    }
                    Button(
                        onClick = { displayCompareAthletes = true
                            searchFCViewModel.get_athlete_attributes_for_comp(token,searchFCViewModel.compareList[0]?.user_id ?: 0, searchFCViewModel.compareList[1]?.user_id ?: 0 )
                                  },
                        modifier = Modifier.height(50.dp).fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                            contentColor = button_text_color)
                    ) {Text("Compare this 2 athletes", fontWeight = FontWeight.Bold)}

                }


            }
        }

        if (displayCompareAthletes) {
            AlertDialog(
                onDismissRequest = { displayCompareAthletes = false },
                title = { Text("athlete's report") },
                text = {
                    if(searchFCViewModel.compareList.size != 2) {
                        Text("Select 2 athletes to compare",
                            color = Red)
                    } else {
                        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {

                            Row(modifier = Modifier.fillMaxWidth()) {
                                Text(
                                    "${searchFCViewModel.compareList[0]?.first_name} ${searchFCViewModel.compareList[0]?.second_name}",
                                    modifier = Modifier.weight(1f),
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    "VS",
                                    modifier = Modifier.weight(1f),
                                    textAlign = TextAlign.Center,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    "${searchFCViewModel.compareList[1]?.first_name} ${searchFCViewModel.compareList[1]?.second_name}",
                                    modifier = Modifier.weight(1f),
                                    fontWeight = FontWeight.Bold,
                                    textAlign = TextAlign.End
                                )
                            }

                            Spacer(modifier = Modifier.height(8.dp))

                            val attributes = listOf(
                                "Acceleration" to Pair(searchFCViewModel.athlete1_attributes?.acceleration, searchFCViewModel.athlete2_attributes?.acceleration),
                                "Sprint Speed" to Pair(searchFCViewModel.athlete1_attributes?.sprint_speed, searchFCViewModel.athlete2_attributes?.sprint_speed),
                                "Finishing" to Pair(searchFCViewModel.athlete1_attributes?.finishing, searchFCViewModel.athlete2_attributes?.finishing),
                                "Shot Power" to Pair(searchFCViewModel.athlete1_attributes?.shot_power, searchFCViewModel.athlete2_attributes?.shot_power),
                                "Long Shots" to Pair(searchFCViewModel.athlete1_attributes?.long_shots, searchFCViewModel.athlete2_attributes?.long_shots),
                                "Penalties" to Pair(searchFCViewModel.athlete1_attributes?.penalties, searchFCViewModel.athlete2_attributes?.penalties),
                                "Short Pass" to Pair(searchFCViewModel.athlete1_attributes?.short_pass, searchFCViewModel.athlete2_attributes?.short_pass),
                                "Long Pass" to Pair(searchFCViewModel.athlete1_attributes?.long_pass, searchFCViewModel.athlete2_attributes?.long_pass),
                                "Agility" to Pair(searchFCViewModel.athlete1_attributes?.agility, searchFCViewModel.athlete2_attributes?.agility),
                                "Balance" to Pair(searchFCViewModel.athlete1_attributes?.balance, searchFCViewModel.athlete2_attributes?.balance),
                                "Ball Control" to Pair(searchFCViewModel.athlete1_attributes?.ball_control, searchFCViewModel.athlete2_attributes?.ball_control),
                                "Dribbling" to Pair(searchFCViewModel.athlete1_attributes?.dribbling, searchFCViewModel.athlete2_attributes?.dribbling),
                                "Heading Acc" to Pair(searchFCViewModel.athlete1_attributes?.heading_acc, searchFCViewModel.athlete2_attributes?.heading_acc),
                                "Jumping" to Pair(searchFCViewModel.athlete1_attributes?.jumping, searchFCViewModel.athlete2_attributes?.jumping),
                                "Stamina" to Pair(searchFCViewModel.athlete1_attributes?.stamina, searchFCViewModel.athlete2_attributes?.stamina),
                                "Strength" to Pair(searchFCViewModel.athlete1_attributes?.strength, searchFCViewModel.athlete2_attributes?.strength)
                            )

                            attributes.forEach { (name, values) ->
                                Row(modifier = Modifier.fillMaxWidth()) {
                                    Text(text = values.first?.toString() ?: "-", modifier = Modifier.weight(1f))
                                    Text(text = name, modifier = Modifier.weight(1f), textAlign = TextAlign.Center)
                                    Text(text = values.second?.toString() ?: "-", modifier = Modifier.weight(1f), textAlign = TextAlign.End)
                                }
                            }
                        }
                    }
                },
                confirmButton = {},
                dismissButton = {
                    Button(
                        onClick = { displayCompareAthletes = false },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = button_color,
                            contentColor = button_text_color
                        )
                    ) { Text("Back")}
                }
            )
        }

        if (displaySearchedAthletes) {
            AlertDialog(
                onDismissRequest = { displaySearchedAthletes = false },
                title = { Text("Searched athletes") },
                text = {
                    Column(modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState()),verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        for (athlete in searchFCViewModel.athletes) {
                            if (athlete != null) {
                                Card(modifier = Modifier.fillMaxWidth(),elevation = CardDefaults.cardElevation(2.dp)) {
                                    Column(modifier = Modifier.padding(8.dp)) {
                                        Text(
                                            text = "${athlete.first_name} ${athlete.second_name}",
                                            color = fontTextColor,
                                            fontWeight = FontWeight.Bold
                                        )

                                        Row(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                            Button(
                                                modifier = Modifier.weight(1f),
                                                onClick = {athleteToShowInfo = athlete},
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text("Info") }

                                            Button(
                                                modifier = Modifier.weight(1f),
                                                onClick = {searchFCViewModel.get_athlete_attributes(token, athlete.user_id)
                                                    athleteToShowAttributes = athlete
                                                },
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text("Attr") }

                                            val isWatchlisted = watchlistViewModel.athletesWatchlist.any { it.user_id == athlete.user_id }
                                            Button(
                                                onClick = {
                                                    if (isWatchlisted) watchlistViewModel.delete_from_watchlist(token, athlete)
                                                    else watchlistViewModel.add_to_watchlist(token, athlete)
                                                },
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text(if (isWatchlisted) "</3" else "<3") }
                                        }
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

        if (athleteToShowInfo != null) {
            val currentAthlete = athleteToShowInfo!!
            AlertDialog(
                onDismissRequest = { athleteToShowInfo = null },
                title = { Text("${currentAthlete.first_name} ${currentAthlete.second_name}") },
                text = {
                    Column(horizontalAlignment = Alignment.End) {
                        ProfileInfoRow("Age", "${currentAthlete.age} ani")
                        ProfileInfoRow("Height", "${currentAthlete.height}")
                        ProfileInfoRow("Weight", "${currentAthlete.weight}")
                        ProfileInfoRow("Weak foot", currentAthlete.weak_foot)
                        ProfileInfoRow("Date of birth", SimpleDateFormat("dd.MM.yyyy", Locale.getDefault()).format(currentAthlete.date_of_birth))
                        ProfileInfoRow("Gender", currentAthlete.gender)
                        ProfileInfoRow("Country", currentAthlete.country)
                        ProfileInfoRow("Region", currentAthlete.region)
                        ProfileInfoRow("City", currentAthlete.city)
                        ProfileInfoRow("Phone number", currentAthlete.phone_number)
                    }
                },
                confirmButton = {},
                dismissButton = {
                    Button(
                        onClick = { athleteToShowInfo = null },
                        colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                    ) { Text("Back") }
                }
            )
        }

        if (athleteToShowAttributes != null) {
            val currentAthlete = athleteToShowAttributes!!
            AlertDialog(
                onDismissRequest = { athleteToShowAttributes = null },
                title = { Text("${currentAthlete.first_name} ${currentAthlete.second_name}") },
                text = {
                    Column(modifier = Modifier.padding(end = 8.dp).verticalScroll(rememberScrollState())) {
                        AttributeStat("Acceleration", searchFCViewModel.athlete_attributes?.acceleration?.toString() ?: "-")
                        AttributeStat("Sprint Speed", searchFCViewModel.athlete_attributes?.sprint_speed?.toString() ?: "-")
                        AttributeStat("Finishing", searchFCViewModel.athlete_attributes?.finishing?.toString() ?: "-")
                        AttributeStat("Shot Power", searchFCViewModel.athlete_attributes?.shot_power?.toString() ?: "-")
                        AttributeStat("Long Shots", searchFCViewModel.athlete_attributes?.long_shots?.toString() ?: "-")
                        AttributeStat("Penalties", searchFCViewModel.athlete_attributes?.penalties?.toString() ?: "-")
                        AttributeStat("Short Pass", searchFCViewModel.athlete_attributes?.short_pass?.toString() ?: "-")
                        AttributeStat("Long Pass", searchFCViewModel.athlete_attributes?.long_pass?.toString() ?: "-")
                        AttributeStat("Agility", searchFCViewModel.athlete_attributes?.agility?.toString() ?: "-")
                        AttributeStat("Balance", searchFCViewModel.athlete_attributes?.balance?.toString() ?: "-")
                        AttributeStat("Ball Control", searchFCViewModel.athlete_attributes?.ball_control?.toString() ?: "-")
                        AttributeStat("Dribbling", searchFCViewModel.athlete_attributes?.dribbling?.toString() ?: "-")
                        AttributeStat("Heading Acc", searchFCViewModel.athlete_attributes?.heading_acc?.toString() ?: "-")
                        AttributeStat("Jumping", searchFCViewModel.athlete_attributes?.jumping?.toString() ?: "-")
                        AttributeStat("Stamina", searchFCViewModel.athlete_attributes?.stamina?.toString() ?: "-")
                        AttributeStat("Strength", searchFCViewModel.athlete_attributes?.strength?.toString() ?: "-")
                    }
                },
                confirmButton = {},
                dismissButton = {
                    Button(
                        onClick = { athleteToShowAttributes = null },
                        colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                    ) { Text("Back") }
                }
            )
        }
    }
    LaunchedEffect(Unit) {
        watchlistViewModel.get_watchlist(token)
    }
}