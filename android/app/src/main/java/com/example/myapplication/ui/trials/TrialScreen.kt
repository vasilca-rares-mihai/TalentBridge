package com.example.myapplication.ui.trials

import android.util.Log
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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.Trial
import com.example.myapplication.ui.profile.ProfileViewModel
import com.example.myapplication.ui.theme.Green
import com.example.myapplication.ui.theme.LightGreen
import com.example.myapplication.ui.theme.LightRed
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import com.example.myapplication.ui.trials.TrialViewModel
import java.text.SimpleDateFormat
import java.util.Locale
import kotlin.collections.component1
import kotlin.collections.component2

// atributele active (restul raman in DB, dar nu se afiseaza)
private val ACTIVE_ATTRS = setOf(
    "strength", "jumping", "acceleration", "sprint_speed",
    "agility", "balance", "dribbling", "finishing"
)

@Composable
fun TrialScreen(token: String, trialViewModel: TrialViewModel, profileViewModel : ProfileViewModel, modifier: Modifier = Modifier) {

    var selectedTrial by remember { mutableStateOf<Trial?>(null) }

    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(top = 60.dp, start = 16.dp, end = 16.dp).fillMaxWidth().verticalScroll(rememberScrollState())) {
            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column( modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Trials",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    for (trial in trialViewModel.trials) {
                        if (trial != null) {

                            HorizontalDivider(modifier = Modifier.padding(vertical = 5.dp))
                            Text(text = trial.football_club,color = fontTextColor)
                            Text(text = trial.country,color = fontTextColor)
                            Text(text = "Trial end date: ${ SimpleDateFormat("dd.MM.yyyy",Locale.getDefault()).format(trial.until_date) }",
                                color = fontTextColor
                            )
                            Text(text = trial.info, color = fontTextColor,)
                            Row() {
                                Button(
                                    onClick = { selectedTrial = trial },
                                    modifier = Modifier.height(50.dp).weight(0.78f), //78
                                    colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                        contentColor = button_text_color)
                                ) {
                                    Text("Show requested attributes")
                                }
                                Spacer(modifier = Modifier.weight(0.02f))
                                if (trial.id_trial in trialViewModel.athlete_trials_applications) {
                                    Button(
                                        onClick = {trialViewModel.delete_trial_application(token, trial.id_trial)},
                                        modifier = Modifier.height(50.dp).weight(0.33f),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = Green,
                                            contentColor = button_text_color
                                        )
                                    ) {
                                        Text("Done")
                                    }
                                } else {
                                    Button(
                                        onClick = { trialViewModel.applyTrial(token, trial.id_trial) },
                                        modifier = Modifier.height(50.dp).weight(0.33f),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = button_color,
                                            contentColor = button_text_color
                                        )
                                    ) {
                                        Text("Apply")
                                    }
                                }

                            }
                        }
                    }
                }
            }

        }
        if (selectedTrial != null) {
            val currentTrial = selectedTrial!!
            AlertDialog(
                onDismissRequest = { selectedTrial = null },
                title = { Text("Requested attributes") },
                text = {
                    Column {currentTrial.requirements.toMap().filterKeys { it in ACTIVE_ATTRS }.forEach { (attr, requiredValue) ->

                        val athleteValue = profileViewModel.attribute?.getFieldValue(attr) ?: 0
                        val cardColor = if (athleteValue < requiredValue) LightRed else LightGreen
                        Card(modifier = Modifier.padding(4.dp).fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = cardColor) ) {
                            Row(modifier = Modifier.padding(4.dp), horizontalArrangement = Arrangement.Center ) {
                                Text(
                                    text = attr.replace("_", " ").replaceFirstChar { it.uppercase() },
                                    color = fontTextColor
                                )

                                Text(
                                    text = " $requiredValue (${profileViewModel.attribute?.getFieldValue(attr) ?: "-"})",
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
                        onClick = { selectedTrial = null },
                        colors = ButtonDefaults.buttonColors(containerColor = button_color,
                            contentColor = button_text_color)
                    ) { Text("Back") }
                }
            )
        }

    }


    LaunchedEffect(Unit) {
        trialViewModel.loadTrials(token)
        trialViewModel.my_trials_applications(token)
    }
}