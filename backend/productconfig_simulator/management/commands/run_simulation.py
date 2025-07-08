#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from productconfig_simulator.utils.simulators import run_simulation

class Command(BaseCommand):
    help = "Verilen simulation_id ile simülasyon işini çalıştırır."

    def add_arguments(self, parser):
        parser.add_argument(
            "simulation_id",
            type=int,
            help="Çalıştırılacak simülasyon işinin ID'si"
        )
        parser.add_argument(
            "--parallel",
            action="store_true",
            help="Simülasyonu paralel modda çalıştırır."
        )
        parser.add_argument(
            "--max_workers",
            type=int,
            default=4,
            help="Paralel modda kullanılacak maksimum işçi sayısı (varsayılan: 4)."
        )

    def handle(self, *args, **options):
        simulation_id = options["simulation_id"]
        parallel = options["parallel"]
        max_workers = options["max_workers"]

        self.stdout.write(f"Simülasyon işini başlatıyor: ID={simulation_id}, parallel={parallel}, max_workers={max_workers}")

        success = run_simulation(simulation_id, parallel=parallel, max_workers=max_workers)
        if success:
            self.stdout.write(self.style.SUCCESS("Simülasyon başarıyla tamamlandı."))
        else:
            raise CommandError("Simülasyon çalıştırılırken bir hata oluştu.")
