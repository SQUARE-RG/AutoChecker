constexpr int kMaxAttempts = 5;
#define MAX_ATTEMPTS kMaxAttempts

int main()
{
    int attempts = 0;
    while (attempts < MAX_ATTEMPTS)
    {
        ++attempts;
    }
    return attempts == kMaxAttempts ? 0 : 1;
}
