package com.example.myapplication.data.network

import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.data.model.AthleteFilters
import com.example.myapplication.data.model.AthleteResponse
import com.example.myapplication.data.model.AthleteUpdate
import com.example.myapplication.data.model.Attribute
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.data.model.CountResponse
import com.example.myapplication.data.model.CreateAthleteRequest
import com.example.myapplication.data.model.CreateFootballClubRequest
import com.example.myapplication.data.model.FcFilters
import com.example.myapplication.data.model.FootballClubData
import com.example.myapplication.data.model.FootballClubResponse
import com.example.myapplication.data.model.LeaderboardInfo
import com.example.myapplication.data.model.LoginData
import com.example.myapplication.data.model.LoginResponse
import com.example.myapplication.data.model.Trial
import com.example.myapplication.data.model.UpdatePassword
import com.google.gson.annotations.SerializedName
import okhttp3.MultipartBody
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query
import retrofit2.http.Streaming

interface TalentBridgeApi {
    @GET("api/athlete/me")
    suspend fun getUserInfo(
        @Header("Authorization") token: String,
        @Query("id_athlete") idAthlete: Int
    ): AthleteResponse

    @GET("api/athlete/attributes/me")
    suspend fun get_athlete_attribute(
        @Header("Authorization") token : String,
        @Query("id_athlete") idAthlete: Int
    ): List<Attribute>

    @PUT("api/athlete/update/me")
    suspend fun update_athlete_info(
        @Header("Authorization") token: String,
        @Body athlete_info: AthleteUpdate
    ): Response<Unit>

    @Multipart
    @POST("api/athlete/video/upload")
    suspend fun upload_video(
        @Header("Authorization") token: String,
        @Query("id_challenge") challenge_id: Int,
        @Part file: MultipartBody.Part
    ): Response<Unit>

    @Streaming
    @GET("api/athlete/video/display/{challenge_id}")
    suspend fun display_video(
        @Header("Authorization") token: String,
        @Path("result_id") resultId: Int
    ): Response<ResponseBody>

    data class StatusResponse(
        @SerializedName("status")
        val status: String
    )
    @GET("api/athlete/video/status/{challenge_id}")
    suspend fun check_analysis_status(
        @Header("Authorization") token: String,
        @Path("challenge_id") challengeId: Int
    ): Response<StatusResponse>

    @POST("api/athlete/video/analyze")
    suspend fun analyze_video(
        @Header("Authorization") token: String,
        @Query("id_challenge") challenge_id: Int
    ): Response<Unit>

    data class AnalysisSummary(
        @SerializedName("exercise") val exercise: String? = null,
        @SerializedName("reps") val reps: Int? = null,
        @SerializedName("correct") val correct: Int? = null,
        @SerializedName("total") val total: Int? = null,
        @SerializedName("accuracy") val accuracy: Double? = null,
        @SerializedName("mistakes") val mistakes: Map<String, Int>? = null,
        @SerializedName("best_distance_m") val bestDistanceM: Double? = null,
        @SerializedName("speed_ms") val speedMs: Double? = null
    )

    @GET("api/athlete/video/summary/{challenge_id}")
    suspend fun get_summary(
        @Header("Authorization") token: String,
        @Path("challenge_id") challengeId: Int
    ): Response<AnalysisSummary>

    @GET("api/athlete/completed_challenges")
    suspend fun get_completed_challenges(
        @Header("Authorization") token: String
    ): Response<List<Int>>

    @GET("api/athlete/video/raw_exists/{challenge_id}")
    suspend fun raw_video_exists(
        @Header("Authorization") token: String,
        @Path("challenge_id") challengeId: Int
    ): Response<Boolean>

    @DELETE("api/athlete/delete/{user_id}")
    suspend fun delete_athlete(
        @Header("Authorization") token: String
    ): Response<Unit>

    @GET("api/athlete/challenges")
    suspend fun get_challenges(
        @Header("Authorization") token: String,
        @Query("index") index: Int
    ): Response<List<Challenge>>

    @GET("api/athlete/challenges/{challenge_id}/leaderboard")
    suspend fun get_leaderboard(
        @Header("Authorization") token: String,
        @Query("challenge_id") challenge_id: Int
    ): Response<List<LeaderboardInfo>>

    @POST("api/athlete/trial/apply/{id_trial}")
    suspend fun apply_trial(
        @Header("Authorization") token: String,
        @Path("id_trial") trialId: Int
    ): Response<Unit>

    @DELETE("api/athlete/delete/trial/application/{id_trial}")
    suspend fun delete_trial_application(
        @Header("Authorization") token: String,
        @Path("id_trial") trialId: Int
    ): Response<Unit>

    @GET("api/athlete/all_trials")
    suspend fun get_trials(
        @Header("Authorization") token: String,
    ): Response<List<Trial>>

    @GET("api/athlete/trial/my_applications")
    suspend fun get_my_applications(
        @Header("Authorization") token: String
    ): Response<List<Int>>








    @GET("api/football_club/trial/applications/{id_trial}")
    suspend fun get_trial_athletes(
        @Header("Authorization") token: String,
        @Path("id_trial") trialId: Int
    ): Response<List<AthleteData>>


    @DELETE("api/football_club/delete/trial")
    suspend fun delete_trial(
        @Header("Authorization") token: String,
        @Query("id_trial") trialId: Int
    ): Response<Unit>

    @GET("api/football_club/me")
    suspend fun getFootballClubInfo(
        @Header("Authorization") token: String,
    ): FootballClubResponse

    @GET("api/athletes")
    suspend fun getAthletes(
        @Header("Authorization") token: String,
    ): List<AthleteData>

    @GET("api/football_club/my_trials")
    suspend fun get_my_trials(
        @Header("Authorization") token: String,
    ): List<Trial>

    @POST("api/football_club/publish/trial")
    suspend fun publish_trial(
        @Header("Authorization") token: String,
        @Body trial: Trial?
    ): Response<Trial>




    @GET("api/football_club/my_watchlist")
    suspend fun getWatchlist(
        @Header("Authorization") token: String,
    ): List<AthleteData>

    @POST("api/football_club/scouting/watchlist/{athlete_id}")
    suspend fun add_to_watchlist(
        @Header("Authorization") token: String,
        @Path("athlete_id") athlete_id: Int
    ): Response<Unit>

    @DELETE("api/football_club/scouting/watchlist/{athlete_id}")
    suspend fun delete_from_watchlist(
        @Header("Authorization") token: String,
        @Path("athlete_id") athlete_id: Int
    ): Response<Unit>


    @POST("api/football_club/search/athlete")
    suspend fun search_athletes(
        @Header("Authorization") token: String,
        @Body athleteFilters: AthleteFilters
    ): Response<List<AthleteData>>



    @PUT("api/football_club/update/me")
    suspend fun update_football_club_info(
        @Header("Authorization") token: String,
        @Body football_club_info: FootballClubData
    ): Response<Unit>



    @POST("api/unauthenticated/login")
    suspend fun login(
        @Query("email") email: String,
        @Query("password") password: String
    ): LoginResponse

    @POST("api/unauthenticated/logout")
    suspend fun logout(
        @Header("Authorization") token: String
    ): Response<Unit>

    @GET()


    @PUT("api/user/update/email")
    suspend fun update_email(
        @Header("Authorization") token: String,
        @Body request: LoginData
    ): String

    @PUT("api/user/update/password")
    suspend fun update_password(
        @Header("Authorization") token: String,
        @Body password: UpdatePassword
    ): Response<Unit>

    @POST("api/unauthenticated/create/athlete")
    suspend fun create_athlete(
        @Body request: CreateAthleteRequest
    ): Response<Unit>

    @POST("api/unauthenticated/create/football_club")
    suspend fun create_football_club(
        @Body request: CreateFootballClubRequest
    ): Response<Unit>

    @GET("api/admin/count_athlete")
    suspend fun info_pannel(
        @Header("Authorization") token: String,
    ): Response<CountResponse>

    @POST("/api/create/challenge")
    suspend fun create_challenge(
        @Header("Authorization") token: String,
        @Body challenge: Challenge?
    ): Response<Unit>


    @DELETE("api/delete/challenge/{challenge_id}")
    suspend fun delete_challenge(
        @Header("Authorization") token: String,
        @Path("challenge_id") challengeId: Int
    ): Response<Unit>


    @POST("api/search/fc")
    suspend fun search_fc(
        @Header("Authorization") token: String,
        @Body fcFilters: FcFilters
    ): Response<List<FootballClubData>>

    @DELETE("api/admin/delete/account")
    suspend fun delete_account(
        @Header("Authorization") token: String,
        @Query("user_id") user_id: Int
    ): Response<Unit>


}