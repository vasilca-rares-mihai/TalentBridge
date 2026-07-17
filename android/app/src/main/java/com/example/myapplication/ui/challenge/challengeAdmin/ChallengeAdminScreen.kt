package com.example.myapplication.ui.challenge.challengeAdmin

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_red_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor

@Composable
fun ChallengeAdminScreen(token: String, challengeAdminViewModel: ChallengeAdminViewModel, modifier: Modifier = Modifier) {

    var challengeCreated by  remember{mutableStateOf<Challenge?>(null)}
    var displayCreateChallenge by remember { mutableStateOf(false)}
    var displayDelete by remember { mutableStateOf(false)}
    var currentChallenge_id by remember { mutableStateOf(0) }

    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(vertical = 60.dp, horizontal = 16.dp).fillMaxWidth().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {

            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Create a new challenge",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    Button(
                        onClick = {
                            challengeCreated = Challenge()
                            displayCreateChallenge = true
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = button_color,
                            contentColor = button_text_color
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Create")
                    }
                }

            }
            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Challenges",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    for (challengeItem in challengeAdminViewModel.challenges) {
                        if (challengeItem != null) {
                            val challenge = challengeItem

                            Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), horizontalArrangement = Arrangement.SpaceBetween ) {

                                Text(text = challenge.challenge_name, color = fontTextColor,)

                                Button(onClick = { displayDelete = true;
                                    currentChallenge_id = challenge.id_challenge},
                                    colors = ButtonDefaults.buttonColors(containerColor = button_red_color,
                                        contentColor = button_text_color)
                                ) {
                                    Text("Delete")
                                }
                            }
                        }
                    }
                }


            }
        }
        if (displayCreateChallenge && challengeCreated != null) {

            AlertDialog(
                onDismissRequest = { displayCreateChallenge = false },
                title = { Text("Create a new challenge") },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedTextField(
                            value = challengeCreated!!.challenge_name,
                            onValueChange = {
                                challengeCreated =
                                    challengeCreated!!.copy(challenge_name = it)
                            },
                            label = { Text("Challenge name") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = challengeCreated!!.unit_of_measure,
                            onValueChange = {
                                challengeCreated =
                                    challengeCreated!!.copy(unit_of_measure = it)
                            },
                            label = { Text("Unit of measure") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )

                        OutlinedTextField(
                            value = challengeCreated!!.info,
                            onValueChange = {
                                challengeCreated =
                                    challengeCreated!!.copy(info = it)
                            },
                            label = { Text("Info") },
                            textStyle = TextStyle(color = fontTextColor),
                            modifier = Modifier.fillMaxWidth()
                        )
                    }


                },
                confirmButton = {
                    Button(
                        onClick = { challengeAdminViewModel.createChallenge(token, challengeCreated);
                            displayCreateChallenge = false},
                        colors = ButtonDefaults.buttonColors(
                            containerColor = button_color,
                            contentColor = button_text_color
                        )
                    ) { Text("Create") }},
                dismissButton = {
                    Button(
                        onClick = { displayCreateChallenge = false},
                        colors = ButtonDefaults.buttonColors(
                            containerColor = button_color,
                            contentColor = button_text_color
                        )
                    ) { Text("Back") }
                }
            )
        }

        if (displayDelete == true) {
            AlertDialog(
                onDismissRequest = { displayDelete = false },
                title = { Text("Are you sure you want to delete this challenge?") },
                text = {},
                confirmButton = {
                    Button(
                        onClick = { challengeAdminViewModel.deleteChallenge(token, currentChallenge_id);
                            displayDelete = false},
                        colors = ButtonDefaults.buttonColors(
                            containerColor = button_red_color,
                            contentColor = button_text_color
                        )
                    ) { Text("Yes") }},
                dismissButton = {
                    Button(
                        onClick = { displayDelete = false},
                        colors = ButtonDefaults.buttonColors(
                            containerColor = button_color,
                            contentColor = button_text_color
                        )
                    ) { Text("Back") }
                }
            )
        }
        LaunchedEffect(Unit) {
            challengeAdminViewModel.loadChallenges(token)
        }
    }
}