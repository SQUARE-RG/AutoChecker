constexpr int bounded_sum(int limit) {
    int sum = 0;
    int i = 0;
    while (1) {
        if (i >= limit) {
            break;
        }
        sum += i;
        ++i;
    }
    return sum;
}

static_assert(bounded_sum(4) == 6);

int main() {
    return bounded_sum(4) == 6 ? 0 : 1;
}
