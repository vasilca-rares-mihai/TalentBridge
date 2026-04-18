package com.example.myapplication.ui.leaderboard

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.data.network.RetrofitClient
import com.example.myapplication.ui.getUserIdFromToken
import com.example.myapplication.ui.leaderboard.LeaderboardScreen
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import java.text.SimpleDateFormat
import java.util.Locale

@Composable
fun LeaderboardScreen(token: String, leaderboardViewModel : LeaderboardViewModel, modifier: Modifier = Modifier) {
    var challenge by remember { mutableStateOf<Challenge?>(null) }
    var color by remember {mutableStateOf(mutableMapOf(1 to Color(0xFFFFD700), 2 to Color(0xFFC0C0C0), 3 to Color(0xFFCD7F32)))}
    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(vertical = 60.dp, horizontal = 16.dp).fillMaxWidth()) {

            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {

                    Text(
                        text = "Clasament",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.SansSerif,
                        modifier = Modifier.padding(bottom = 16.dp),
                        color = fontTextColor,
                    )
                    Row(modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(bottom = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Spacer(modifier = Modifier.height(5.dp))
                        for (i in 0 until leaderboardViewModel.challenges.size) {
                            val challengeItem = leaderboardViewModel.challenges[i]
                            if (challengeItem != null) {
                                Button(
                                    onClick = {
                                        challenge = challengeItem
                                        leaderboardViewModel.actualChallenge = challengeItem.id_challenge
                                        leaderboardViewModel.loadLeaderboard(token,leaderboardViewModel.actualChallenge)
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = button_color,contentColor = button_text_color), modifier = Modifier) {
                                    Text(challengeItem.challenge_name)
                                }
                            }
                        }
                    }
                    Column( modifier = Modifier.fillMaxWidth().weight(1f).verticalScroll(rememberScrollState()),verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (leaderboardViewModel.topAthletes.isEmpty()) {
                            Text(
                                text = "There are no results at the moment.",
                                style = MaterialTheme.typography.bodyMedium,
                                color = fontTextColor,
                                modifier = Modifier.padding(top = 16.dp)
                            )
                        } else {
                            for (i in 0 until leaderboardViewModel.topAthletes.size) {
                                val athlete = leaderboardViewModel.topAthletes[i]
                                if (athlete != null) {
                                    val rank = i + 1
                                    val culoareBulina = color[rank] ?: Color(0xFFE0E0E0)
                                    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp, horizontal = 4.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Box( modifier = Modifier.size(32.dp).clip(CircleShape).background(culoareBulina),contentAlignment = Alignment.Center ) {
                                                Text(
                                                    text = "$rank",
                                                    fontWeight = FontWeight.Bold,
                                                    color = fontTextColor
                                                )
                                            }
                                            Text(
                                                text = "${athlete.first_name} ${athlete.second_name}",
                                                style = MaterialTheme.typography.bodyLarge,
                                                fontWeight = FontWeight.Bold,
                                                color = fontTextColor
                                            )
                                        }
                                        Column(horizontalAlignment = Alignment.End) {
                                            Text(
                                                text = athlete.result_value.toString(),
                                                fontWeight = FontWeight.Bold,
                                                color = fontTextColor
                                            )
                                            Text(
                                                text = SimpleDateFormat(
                                                    "dd.MM.yyyy",
                                                    Locale.getDefault()
                                                ).format(athlete.date_recorded),
                                                color = fontTextColor
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                LaunchedEffect(Unit) {
                    val realUserId = getUserIdFromToken(token)
                    leaderboardViewModel.loadLeaderboard(token, realUserId)

                }
            }
        }
    }
}
