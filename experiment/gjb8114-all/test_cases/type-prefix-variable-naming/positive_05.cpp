// positive_05.cpp
// Intent: const-qualified local variables all use correct type prefixes.
long compute(long lBase) {
    const long lMaxRetries = 3;
    const unsigned int uiThreshold = 2U;
    const double dScale = 1.5;
    const char cSeparator = ';';
    return lBase + lMaxRetries + static_cast<long>(uiThreshold) + static_cast<long>(dScale) + static_cast<long>(cSeparator);
}

int main() {
    return static_cast<int>(compute(4));
}
