#define FEATURE_ENABLED 1

#if FEATURE_ENABLED
constexpr int kLimit = 7;
#endif /* FEATURE_ENABLED */

int main() {
#if FEATURE_ENABLED
    return kLimit;
#else
    return 0;
#endif
}
