// positive_06.cpp
int main() {
    int i = 0;
    int sum = 0;
    do {
        sum += i;
        i++;
        if (i == 3) {
            goto finish;
        }
    } while (i < 10);
finish:
    return sum;
}
