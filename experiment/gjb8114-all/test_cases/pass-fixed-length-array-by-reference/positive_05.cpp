template <int N>
void increment(int (&values)[N])
{
    for (int i = 0; i < N; ++i) {
        values[i] += 1;
    }
}

int main() {
    int data[6] = {0, 1, 2, 3, 4, 5};
    increment(data);
    return 0;
}
