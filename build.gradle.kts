import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import org.ajoberstar.grgit.Grgit
import org.redline_rpm.header.Os

group = "espn-ffb"
version = "0.0.1-SNAPSHOT"

val buildNumber: String by project

val git: Grgit = Grgit.open()
val timestamp: String = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd.HHmmss"))
val prefix = if (git.branch.current().name == "master") "1" else "0.rc.$timestamp"
val gitHash = git.head().abbreviatedId!!

plugins {
    val grgitVersion = "3.1.1"
    val ospackageVersion = "6.1.1"

    id("org.ajoberstar.grgit") version grgitVersion
    id("nebula.ospackage") version ospackageVersion
}

tasks.buildDeb {
    addParentDirs = false
    version = project.version.toString().replace("-SNAPSHOT", "")
    release = "$prefix+$buildNumber.$gitHash"

    val logDir = "/var/log/$packageName"
    directory(logDir)
}

ospackage {
    os = Os.LINUX
    user = "raph"
    group = "www-data"

    packageName = project.name

    val packageDir = "$projectDir/espn_ffb"
    val localConfigDir = "$projectDir/conf"
    val localSystemdDir = "$projectDir/ospackage/systemd"
    val controlDir = "$projectDir/ospackage/scripts"

    val deployDir = "/opt/$packageName/espn_ffb"
    val configDir = "/etc/opt/$packageName"
    val systemdDir = "/usr/lib/systemd/system"

    ospackage.from(packageDir).exclude("__pycache__").into(deployDir)
    ospackage.from(localConfigDir).include("*").into(configDir)
    ospackage.from(localSystemdDir).into(systemdDir)
    postInstall(File("$controlDir/postinst.sh"))
}