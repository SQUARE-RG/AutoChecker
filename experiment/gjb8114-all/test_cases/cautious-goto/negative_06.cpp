int classify(int code) {
  int result = 0;
  switch (code) {
  case 1:
    result = 1;
    goto case_two; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-5-1]
  case 2:
  case_two:
    result += 2;
    break;
  default:
    result = 3;
  }
  return result;
}
