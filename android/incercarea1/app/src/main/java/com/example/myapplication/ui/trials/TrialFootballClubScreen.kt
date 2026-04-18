package com.example.myapplication.ui.trials

import DatePickerField
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
import androidx.compose.material3.HorizontalDivider
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
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.Attribute
import com.example.myapplication.data.model.Trial
import com.example.myapplication.ui.profile.AttributeStat
import com.example.myapplication.ui.profile.ProfileInfoRow
import com.example.myapplication.ui.profile.ProfileViewModel
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_red_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import com.example.myapplication.ui.watchlist.WatchlistViewModel
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.collections.component1
import kotlin.collections.component2

@Composable
fun TrialFootballClubScreen(token: String, trialViewModel: TrialViewModel, watchlistViewModel: WatchlistViewModel, modifier: Modifier = Modifier) {

    var selectedTrialRequirements by remember { mutableStateOf<Trial?>(null) }
    var selectedTrialAthletes by remember { mutableStateOf<Trial?>(null) }
    var displayCreateTrial by remember { mutableStateOf(false) }
    var trialToDelete by remember { mutableStateOf<Trial?>(null) }

    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(top = 60.dp, start = 16.dp, end = 16.dp).fillMaxWidth().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {

                    Text(
                        text = "Create a trial",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    Button(onClick = {trialViewModel.createdTrial = Trial(
                        id_trial = 0,
                        until_date = Date(),
                        info = "",
                        requirements = Attribute(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                        football_club = "",
                        country = ""
                    )
                        displayCreateTrial = true},
                        modifier = Modifier.height(50.dp).fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                            contentColor = button_text_color)) { Text("Click here") }
                }


            }
            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column( modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Your trials",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    for (trial in trialViewModel.fc_my_trials) {
                        if (trial != null) {
                            HorizontalDivider(modifier = Modifier.padding(vertical = 5.dp))
                            Text(text = "Trial end date: ${SimpleDateFormat("dd.MM.yyyy",Locale.getDefault()).format(trial.until_date)}",
                                color = fontTextColor)
                            Text(text = trial.info, color = fontTextColor,)
                                Button(
                                    onClick = { selectedTrialRequirements = trial },
                                    modifier = Modifier.height(50.dp).fillMaxWidth(),
                                    colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                        contentColor = button_text_color)
                                ) {Text("Show requested attributes") }
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                    Button(
                                        onClick = { trialViewModel.my_trial_applicants(token, trial.id_trial); selectedTrialAthletes = trial },
                                        modifier = Modifier.height(50.dp).weight(2f),
                                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                            contentColor = button_text_color)
                                    ) {Text("Trial applications") }
                                    Button(
                                        onClick = {trialToDelete = trial },
                                        modifier = Modifier.height(50.dp).weight(1f),
                                        colors = ButtonDefaults.buttonColors(containerColor = button_red_color,
                                            contentColor = button_text_color)
                                    ) {Text("Delete") }
                                }

                                Spacer(modifier = Modifier.weight(0.02f))

                        }
                    }
                }
            }

        }
        if (selectedTrialRequirements != null) {
            val currentTrial = selectedTrialRequirements!!
            AlertDialog(
                onDismissRequest = { selectedTrialRequirements = null },
                title = { Text("Requested attributes") },
                text = {
                    Column {
                        currentTrial.requirements.toMap().forEach { (attr, requiredValue) ->
                            Card(modifier = Modifier.padding(4.dp).fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp)) {
                                Row(modifier = Modifier.padding(4.dp), horizontalArrangement = Arrangement.Center ) {
                                    Text(
                                        text = attr.replace("_", " ").capitalize(),
                                        color = fontTextColor
                                    )
                                    Text(
                                        text = "$requiredValue",
                                        fontWeight = FontWeight.Bold,
                                        color = fontTextColor
                                    )
                                }
                            }
                        }
                    }
                },
                confirmButton = {},
                dismissButton = {
                    Button(
                        onClick = { selectedTrialRequirements = null },
                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                            contentColor = button_text_color)
                    ) { Text("Back") }
                }
            )
        }
        var athleteToShowInfo by remember { mutableStateOf<AthleteData?>(null) }
        var athleteToShowAttributes by remember { mutableStateOf<AthleteData?>(null) }

        if (selectedTrialAthletes != null) {
            AlertDialog(
                onDismissRequest = { selectedTrialAthletes = null },
                title = { Text("Trial athletes") },
                text = {
                    Column(modifier = Modifier.fillMaxWidth(),verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        for (athlete in trialViewModel.fc_trial_athletes) {
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
                                                onClick = { athleteToShowInfo = athlete },
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text("Info") }

                                            Button(
                                                modifier = Modifier.weight(1f),
                                                onClick = {
                                                    trialViewModel.get_athlete_attributes(token, athlete.user_id)
                                                    athleteToShowAttributes = athlete
                                                },
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text("Attr") }

                                            val isWatchlisted = watchlistViewModel.athletesWatchlist.any { it?.user_id == athlete.user_id }
                                            Button(onClick = {
                                                    if (isWatchlisted) watchlistViewModel.delete_from_watchlist(token,athlete)
                                                    else watchlistViewModel.add_to_watchlist(token, athlete )
                                                }, colors = ButtonDefaults.buttonColors(
                                                    containerColor = button_color,
                                                    contentColor = button_text_color
                                                )) { Text(if (isWatchlisted) "</3" else "<3") }
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
                        onClick = { selectedTrialAthletes = null },
                        colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                    ) { Text("Back") }
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
                        AttributeStat("Acceleration", trialViewModel.athlete_attributes?.acceleration?.toString() ?: "-")
                        AttributeStat("Sprint Speed", trialViewModel.athlete_attributes?.sprint_speed?.toString() ?: "-")
                        AttributeStat("Finishing", trialViewModel.athlete_attributes?.finishing?.toString() ?: "-")
                        AttributeStat("Shot Power", trialViewModel.athlete_attributes?.shot_power?.toString() ?: "-")
                        AttributeStat("Long Shots", trialViewModel.athlete_attributes?.long_shots?.toString() ?: "-")
                        AttributeStat("Penalties", trialViewModel.athlete_attributes?.penalties?.toString() ?: "-")
                        AttributeStat("Short Pass", trialViewModel.athlete_attributes?.short_pass?.toString() ?: "-")
                        AttributeStat("Long Pass", trialViewModel.athlete_attributes?.long_pass?.toString() ?: "-")
                        AttributeStat("Agility", trialViewModel.athlete_attributes?.agility?.toString() ?: "-")
                        AttributeStat("Balance", trialViewModel.athlete_attributes?.balance?.toString() ?: "-")
                        AttributeStat("Ball Control", trialViewModel.athlete_attributes?.ball_control?.toString() ?: "-")
                        AttributeStat("Dribbling", trialViewModel.athlete_attributes?.dribbling?.toString() ?: "-")
                        AttributeStat("Heading Acc", trialViewModel.athlete_attributes?.heading_acc?.toString() ?: "-")
                        AttributeStat("Jumping", trialViewModel.athlete_attributes?.jumping?.toString() ?: "-")
                        AttributeStat("Stamina", trialViewModel.athlete_attributes?.stamina?.toString() ?: "-")
                        AttributeStat("Strength", trialViewModel.athlete_attributes?.strength?.toString() ?: "-")
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

        if (trialToDelete != null) {
            AlertDialog(
                onDismissRequest = { trialToDelete = null },
                title = { Text("Are you sure you want to delete this trial?") },
                confirmButton = {
                    Button(onClick = {
                        trialViewModel.delete_trial(token, trialToDelete!!.id_trial)
                        trialToDelete = null
                    },
                        colors = ButtonDefaults.buttonColors(containerColor = button_red_color)) {
                        Text("Yes")
                    }
                },
                dismissButton = {
                    Button(onClick = { trialToDelete = null },
                        colors = ButtonDefaults.buttonColors(containerColor = button_color)
            ) { Text("Back") }
                }
            )
        }


        if (displayCreateTrial) {
            AlertDialog(
                onDismissRequest = { displayCreateTrial = false },
                title = { Text("Create trial") },
                text = {
                    Column(modifier = Modifier.padding(20.dp).verticalScroll(rememberScrollState())) {
                        DatePickerField(
                            label = "Expire date of trial",
                            currentDate = trialViewModel.createdTrial?.until_date ?: Date(),
                            onDateSelected = { newDate ->
                                trialViewModel.createdTrial =
                                    trialViewModel.createdTrial!!.copy(until_date = newDate)
                            }
                        )
                        OutlinedTextField(
                            value = trialViewModel.createdTrial?.info ?: "",
                            onValueChange = { newValue ->
                                trialViewModel.createdTrial = trialViewModel.createdTrial?.copy(info = newValue)
                            },
                            label = { Text("Info") }
                        )
                        val requirementsMap = trialViewModel.createdTrial?.requirements?.toMap() ?: emptyMap()

                        requirementsMap.forEach { (fieldName, value) ->
                            OutlinedTextField(
                                value = if (value == 0) "" else value.toString(),
                                onValueChange = { newValue ->
                                    val cleanValue = newValue.filter { it.isDigit() }
                                    val intValue = cleanValue.toIntOrNull() ?: 0

                                    trialViewModel.updateRequirement(fieldName, intValue)
                                },
                                label = { Text(fieldName.replace("_", " ").capitalize()) },
                                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                singleLine = true,
                                textStyle = TextStyle(color = fontTextColor)
                            )
                        }

                    }

                },
                confirmButton = {
                    Button(
                        onClick = {
                            trialViewModel.publish_trial(token, trialViewModel.createdTrial)
                            displayCreateTrial = false
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = button_color,
                            contentColor = button_text_color
                        )
                    ) {Text("Create trial")}
                },
                dismissButton = {
                    Button(
                        onClick = { displayCreateTrial = false },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = button_color,
                            contentColor = button_text_color
                        )
                    ) { Text("Cancel")}
                }
            )
        }


    }


    LaunchedEffect(Unit) {
        trialViewModel.loadTrials(token)
        trialViewModel.my_trials(token)
        watchlistViewModel.get_watchlist(token)

    }
}