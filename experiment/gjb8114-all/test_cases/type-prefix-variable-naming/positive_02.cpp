int computeLaunch(unsigned int uiLaunchButton, long lLaunchTime, double dLaunchAzim) {
    return static_cast<int>(uiLaunchButton) +
           static_cast<int>(lLaunchTime) +
           static_cast<int>(dLaunchAzim);
}

int main() {
    return computeLaunch(1U, 2L, 3.0);
}
