class LaunchController {
public:
    static int iRetryCount;
    static double dElapsedSeconds;
    static bool bLaunched;
};

int LaunchController::iRetryCount = 0;
double LaunchController::dElapsedSeconds = 0.0;
bool LaunchController::bLaunched = false;

int main() {
    LaunchController::iRetryCount = 2;
    LaunchController::dElapsedSeconds = 1.5;
    LaunchController::bLaunched = true;
    return LaunchController::iRetryCount;
}
