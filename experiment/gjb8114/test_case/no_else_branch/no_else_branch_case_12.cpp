#include <stdio.h>

int evaluate_score(int score) {
    if (score >= 90) {
        return 'A';
    } else if (score >= 80) {
        return 'B';
    } else if (score >= 70) {
        return 'C';
    } else if (score >= 60) {
        return 'D';
    } else {
        return 'F';  // 符合：多个else if后包含else
    }
}

int main(void) {
    printf("%c\n", evaluate_score(85));
    return 0;
}