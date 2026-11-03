int computeTotal(int iBase) {
    static double dElapsedSeconds = 0.0;
    static int iCallCount = 0;
    dElapsedSeconds += 1.0;
    ++iCallCount;
    return iBase + static_cast<int>(dElapsedSeconds) + iCallCount;
}

int main() {
    return computeTotal(1);
}
