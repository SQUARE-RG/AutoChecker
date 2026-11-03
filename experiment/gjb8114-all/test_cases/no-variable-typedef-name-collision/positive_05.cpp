typedef long long Accumulator;
int main() {
    int total = 0;
    {
        long long accumulator = 10;
        total = static_cast<int>(accumulator + 1);
    }
    return total;
}
