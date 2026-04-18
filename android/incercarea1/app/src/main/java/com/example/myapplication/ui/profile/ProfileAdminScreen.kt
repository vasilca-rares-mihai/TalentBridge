package com.example.myapplication.ui.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.example.myapplication.ui.getEmailFromToken
import com.example.myapplication.ui.getRoleFromToken
import com.example.myapplication.ui.getUserIdFromToken
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_red_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import java.text.SimpleDateFormat
import java.util.Locale

@Composable
fun ProfileAdminScreen(token: String, profileViewModel: ProfileViewModel, modifier: Modifier = Modifier, onLogout: () -> Unit) {
    LaunchedEffect(Unit) {
        profileViewModel.infoPannel(token)
    }
    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {

                Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {

                    Text(
                        text = getEmailFromToken(token),
                        style = MaterialTheme.typography.bodyMedium,
                        color = fontTextColor
                    )
                    Badge(modifier = Modifier.padding(top = 8.dp), containerColor = Color(0xFF4CAF50)) {
                        Text(
                            text = getRoleFromToken(token).uppercase(),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }
            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(24.dp)) {
                    Text(
                        text = "Platform information",
                        style = MaterialTheme.typography.titleMedium,
                        color = fontTextColor,
                        fontWeight = FontWeight.Bold
                    )

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        Column(modifier = Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Athletes", color = fontTextColor, textAlign = TextAlign.Center)
                            Text("${profileViewModel.infoPannel.athleteCount}", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        }
                        Column(modifier = Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Football clubs", color = fontTextColor, textAlign = TextAlign.Center)
                            Text("${profileViewModel.infoPannel.footballClubCount}", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        }
                    }

                    HorizontalDivider(modifier = Modifier.padding(vertical = 2.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        Column(modifier = Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Challenges", color = fontTextColor, textAlign = TextAlign.Center)
                            Text("${profileViewModel.infoPannel.challengesCount}", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        }
                        Column(modifier = Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Analysis", color = fontTextColor, textAlign = TextAlign.Center)
                            Text("${profileViewModel.infoPannel.analysisCount}", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        }
                    }

                    HorizontalDivider(modifier = Modifier.padding(vertical = 2.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        Column(modifier = Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Total trials", color = fontTextColor, textAlign = TextAlign.Center)
                            Text("${profileViewModel.infoPannel.trialsCount}", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        }
                        Column(modifier = Modifier.fillMaxWidth(0.5f), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Trial applications", color = fontTextColor, textAlign = TextAlign.Center)
                            Text("${profileViewModel.infoPannel.trialApplicationsCount}", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        }
                    }

                    HorizontalDivider(modifier = Modifier.padding(vertical = 2.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                        Column(modifier = Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Favorite athletes", color = fontTextColor, textAlign = TextAlign.Center)
                            Text("${profileViewModel.infoPannel.favoriteAthCount}", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
            Button(
                    onClick = { profileViewModel.onLogout(token)
                        onLogout()},
                    modifier = Modifier.fillMaxWidth().height(50.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = button_red_color,
                        contentColor = button_text_color)
                ) {
                    Text("Log out")
                }

                Spacer(modifier = Modifier.height(24.dp))


        }
    }
}
