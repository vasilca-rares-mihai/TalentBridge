package com.example.myapplication.data.model
import com.google.gson.annotations.SerializedName
import java.util.Date

data class AthleteResponse(
    val role: String,
    val email: String,
    val athlete: AthleteData
)

data class FootballClubResponse(
    val role: String,
    val email: String,
    val football_club: FootballClubData
)

data class AthleteData(
    val user_id: Int,
    val first_name: String,
    val second_name: String,
    val age: Int,
    val field_position: String,
    val weak_foot: String,
    val gender: String,
    val height: Float,
    val weight: Float,
    val country: String,
    val region: String,
    val city: String,
    val phone_number: String,
    val date_of_birth: Date
)
data class FootballClubData(
    val user_id: Int = 0,
    val name: String = "",
    val country: String = "",
    val info: String = ""
)

data class CreateAthleteRequest(
    val email: String,
    val password: String,
    val athlete_data: AthleteData
)

data class Attribute(
    val id: Int,
    val acceleration: Int,
    val sprint_speed: Int,
    val finishing: Int,
    val shot_power: Int,
    val long_shots: Int,
    val penalties: Int,
    val short_pass: Int,
    val long_pass: Int,
    var agility: Int,
    val balance: Int,
    val ball_control: Int,
    val dribbling: Int,
    val heading_acc: Int,
    val jumping: Int,
    val stamina: Int,
    val strength: Int
){
    fun getFieldValue(fieldName: String): Int {
        return when (fieldName.lowercase().replace(" ", "_")) {
            "acceleration" -> acceleration
            "sprint_speed" -> sprint_speed
            "finishing" -> finishing
            "shot_power" -> shot_power
            "long_shots" -> long_shots
            "penalties" -> penalties
            "short_pass" -> short_pass
            "long_pass" -> long_pass
            "agility" -> agility
            "balance" -> balance
            "ball_control" -> ball_control
            "dribbling" -> dribbling
            "heading_acc" -> heading_acc
            "jumping" -> jumping
            "stamina" -> stamina
            "strength" -> strength
            else -> 0
        }
    }
    fun toMap(): Map<String, Int> {
        return mapOf(
            "acceleration" to acceleration,
            "sprint_speed" to sprint_speed,
            "finishing" to finishing,
            "shot_power" to shot_power,
            "long_shots" to long_shots,
            "penalties" to penalties,
            "short_pass" to short_pass,
            "long_pass" to long_pass,
            "agility" to agility,
            "balance" to balance,
            "ball_control" to ball_control,
            "dribbling" to dribbling,
            "heading_acc" to heading_acc,
            "jumping" to jumping,
            "stamina" to stamina,
            "strength" to strength
        )
    }
}

data class AttributeUpdate(
    val acceleration: Int,
    val sprint_speed: Int,
    val finishing: Int,
    val shot_power: Int,
    val long_shots: Int,
    val penalties: Int,
    val short_pass: Int,
    val long_pass: Int,
    val agility: Int,
    val balance: Int,
    val ball_control: Int,
    val dribbling: Int,
    val heading_acc: Int,
    val jumping: Int,
    val stamina: Int,
    val strength: Int
)


data class LeaderboardInfo(
    val first_name: String,
    val second_name: String,
    val result_value: Int,
    val date_recorded: Date
)


data class LoginResponse(
    val access_token: String
)
enum class FieldPositionsEnum {
    goalkeeper, center_back, full_back, defensive_midfielder, midfielder, attacking_midfielder, winger, attacker
}
enum class WeakFootEnum {
    left, right
}

enum class GenderEnum {
    Male, Female, Other
}



data class UpdatePassword(
    val old_password: String,
    val new_password: String,
    val new_password_confirm: String
)

data class AthleteUpdate(
    var first_name: String,
    var second_name: String,
    var field_position: String,
    var weak_foot: String,
    var height: Float,
    var weight: Float,
    var country: String,
    var region: String,
    var city: String,
    var phone_number: String,
    var date_of_birth: Date
)

data class Challenge(
    val id_challenge: Int = 0,
    val challenge_name: String = "",
    val unit_of_measure: String = "",
    val info: String = ""
)

data class UploadResponse(
    val message: String,
    val saved_path: String,
    val filename: String,
    val athlete_id: Int
)

data class Trial(
    val id_trial: Int,
    val until_date: Date,
    var info: String,
    var requirements: Attribute,
    val football_club: String,
    val country: String
)

enum class AccountType {
    athlete, football_club
}


data class CreateFootballClubRequest(
    val email: String,
    val password: String,
    val club_data: FootballClubData
)

data class LoginData(
    val email: String,
    val password: String
)


data class AthleteFilters(
    val first_name: String = "",
    val second_name: String = "",
    val gender: String = "",
    val field_position: String = "",
    val weak_foot: String = "",
    val country: String = "",
    val age_range: List<Int?>? = listOf(null, null),
    val height_range: List<Float?>? = listOf(null, null),
    val weight_range: List<Float?>? = listOf(null, null)
)

data class FcFilters(
    val name: String = "",
    val country: String = ""
)

data class CountResponse(
    var athleteCount: Int = 0,
    var footballClubCount: Int = 0,
    var analysisCount: Int = 0,
    var challengesCount: Int = 0,
    var trialsCount: Int = 0,
    var favoriteAthCount: Int = 0,
    var trialApplicationsCount: Int = 0,
)