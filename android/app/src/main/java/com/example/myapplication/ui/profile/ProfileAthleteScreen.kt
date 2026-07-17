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
import androidx.compose.ui.unit.dp
import com.example.myapplication.ui.getUserIdFromToken
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_red_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import java.text.SimpleDateFormat
import java.util.Locale

@Composable
fun ProfileAthleteScreen(token: String, profileViewModel: ProfileViewModel, modifier: Modifier = Modifier, onLogout: () -> Unit) {
    LaunchedEffect(Unit) {
        val realUserId = getUserIdFromToken(token)
        profileViewModel.loadAthleteData(token, realUserId)
    }
    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {

            if(profileViewModel.role == "athlete") {
                val currentAthlete = profileViewModel.athlete
                val currentAttributes = profileViewModel.attribute
                Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {

                    if (currentAthlete != null) {
                        Text(
                            text = "${currentAthlete.first_name} ${currentAthlete.second_name}",
                            style = MaterialTheme.typography.headlineMedium,
                            color = fontTextColor,
                            fontWeight = FontWeight.ExtraBold
                        )
                    }
                    Text(
                        text = profileViewModel.email,
                        style = MaterialTheme.typography.bodyMedium,
                        color = fontTextColor
                    )
                    Badge(modifier = Modifier.padding(top = 8.dp), containerColor = Color(0xFF4CAF50)) {
                        Text(
                            text = profileViewModel.role.uppercase(),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }

                if (currentAthlete != null) {
                    Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(
                                text = "Personal information",
                                style = MaterialTheme.typography.titleMedium,
                                modifier = Modifier.padding(bottom = 12.dp),
                                color = fontTextColor,
                            )

                            ProfileInfoRow("Age", "${currentAthlete.age} ani")
                            ProfileInfoRow("Date of birth",SimpleDateFormat("dd.MM.yyyy", Locale.getDefault()).format(currentAthlete.date_of_birth),)
                            ProfileInfoRow("Gender", currentAthlete.gender)
                            ProfileInfoRow("Country", currentAthlete.country)
                            ProfileInfoRow("Region", currentAthlete.region)
                            ProfileInfoRow("City", currentAthlete.city)
                            ProfileInfoRow("Phone number", currentAthlete.phone_number)

                            HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp))

                            Text(
                                text = "Physical & Tactical Profile",
                                style = MaterialTheme.typography.titleMedium,
                                modifier = Modifier.padding(bottom = 12.dp),
                                color = fontTextColor,
                            )
                            ProfileInfoRow("Height", "${currentAthlete.height} m")
                            ProfileInfoRow("Weight", "${currentAthlete.weight} kg")
                            ProfileInfoRow("Field position",currentAthlete.field_position.replaceFirstChar { it.uppercase() })
                            ProfileInfoRow("Weak foot",currentAthlete.weak_foot.replaceFirstChar { it.uppercase() })
                        }
                    }
                }

                if (currentAttributes != null) {
                    Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {

                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(
                                text = "Attribute",
                                style = MaterialTheme.typography.titleMedium,
                                modifier = Modifier.padding(bottom = 12.dp),
                                color = fontTextColor,
                            )

                            Row(modifier = Modifier.fillMaxWidth()) {
                                Column(modifier = Modifier.weight(1f).padding(end = 8.dp)) {
                                    AttributeStat("Strength", currentAttributes.strength.toString())
                                    AttributeStat("Jumping", currentAttributes.jumping.toString())
                                    AttributeStat("Acceleration", currentAttributes.acceleration.toString())
                                    AttributeStat("Sprint Speed", currentAttributes.sprint_speed.toString())
                                }
                                Column(modifier = Modifier.weight(1f).padding(start = 8.dp)) {
                                    AttributeStat("Agility", currentAttributes.agility.toString())
                                    AttributeStat("Balance", currentAttributes.balance.toString())
                                    AttributeStat("Dribbling", currentAttributes.dribbling.toString())
                                    AttributeStat("Finishing", currentAttributes.finishing.toString())
                                }
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
}



@Composable
fun ProfileInfoRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = fontTextColor
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = fontTextColor
        )
    }
}

@Composable
fun AttributeStat(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = fontTextColor
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.ExtraBold,
            color = fontTextColor
        )
    }

}