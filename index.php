<?php
// Konfiguration
$calender_weeg_folders = 'calender_weeks';
$slide_interval = 7; # Seconds
// ==========

if(isset($_GET['slide_interval'])) {
  $slide_interval = intval($_GET['slide_interval']);
}

function get_calender_week() {
    $week = 52;
    $cw = date('W', strtotime(date('Y-m-d')));
    if($cw <= 52) {
        $week = date('W', strtotime(date('Y-m-d')));
    }
    return $week;
}

$images = glob($calender_weeg_folders . DIRECTORY_SEPARATOR . get_calender_week() . DIRECTORY_SEPARATOR . '*');

?>
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <title>Schaukasten</title>
  <!--<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1" />-->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="swiper-bundle.min.css" />
  <style>
    html,
    body {
      position: relative;
      height: 100%;
    }

    body {
      background: #eee;
      font-family: Helvetica Neue, Helvetica, Arial, sans-serif;
      font-size: 14px;
      color: #000;
      margin: 0;
      padding: 0;
    }

    .swiper {
      width: 100%;
      height: 100%;
    }

    .swiper-slide {
      text-align: center;
      font-size: 18px;
      background: #fff;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .swiper-slide img {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  </style>
</head>

<body>
  <!-- Swiper -->
  <div class="swiper mySwiper">
    <div class="swiper-wrapper">
        <?php foreach($images as $img): ?>
            <div class="swiper-slide">
                <img src="<?= $img ?>" />
            </div>
        <?php endforeach; ?>
      <!--<div class="swiper-slide">Slide 1</div>
      <div class="swiper-slide">Slide 2</div>
      <div class="swiper-slide">Slide 3</div>
      <div class="swiper-slide">Slide 4</div>
      <div class="swiper-slide">Slide 5</div>
      <div class="swiper-slide">Slide 6</div>
      <div class="swiper-slide">Slide 7</div>
      <div class="swiper-slide">Slide 8</div>
      <div class="swiper-slide">Slide 9</div>-->
    </div>
    <div class="swiper-pagination"></div>
  </div>

  <script src="swiper-bundle.min.js"></script>

  <script>
    var swiper = new Swiper(".mySwiper", {
      spaceBetween: 30,
      centeredSlides: true,
      autoplay: {
        delay: <?= $slide_interval * 1000 ?>,
        disableOnInteraction: false,
      },
      pagination: {
        el: ".swiper-pagination",
        clickable: true,
      },
    });
  </script>
</body>

</html>
