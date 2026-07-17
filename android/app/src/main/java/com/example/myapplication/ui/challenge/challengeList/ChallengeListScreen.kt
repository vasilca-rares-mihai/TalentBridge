package com.example.myapplication.ui.challenge.challengeList

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
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor

@Composable
fun ChallengeListScreen(token: String, challengeListViewModel: ChallengeListViewModel, onChallengeClick: (Challenge) -> Unit, modifier: Modifier = Modifier) {


    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(vertical = 60.dp, horizontal = 16.dp).fillMaxWidth()) {

            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(modifier = Modifier.padding(20.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Challenges",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.SansSerif,
                        color = fontTextColor
                    )
                    for (challengeItem in challengeListViewModel.challenges) {
                        if (challengeItem != null) {
                            val challenge = challengeItem
                            val done = challenge.id_challenge in challengeListViewModel.completedIds

                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                elevation = CardDefaults.cardElevation(1.dp),
                                colors = CardDefaults.cardColors(
                                    containerColor = if (done) Color(0xFFDCF2DC) else background_color
                                )
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 10.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column {
                                        Text(
                                            text = challenge.challenge_name,
                                            color = fontTextColor,
                                            fontWeight = FontWeight.Bold
                                        )
                                        if (done) {
                                            Text(
                                                text = "Completat",
                                                color = Color(0xFF2E7D32),
                                                style = MaterialTheme.typography.bodySmall
                                            )
                                        }
                                    }

                                    Button(
                                        onClick = { onChallengeClick(challenge) },
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = button_color,
                                            contentColor = button_text_color
                                        )
                                    ) {
                                        Text(if (done) "Vezi rezultatul" else "Start challenge")
                                    }
                                }
                            }
                        }
                    }
                }

                LaunchedEffect(Unit) {
                    challengeListViewModel.loadChallenges(token)
                }
            }
        }
    }
}