constexpr int kSize = 5;

void scale(int (&values)[kSize])
{
    for (int i = 0; i < kSize; ++i) {
        values[i] *= 2;
    }
}

int main() {
    int data[kSize] = {1, 2, 3, 4, 5};
    scale(data);
    return 0;
}
