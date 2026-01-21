import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Props {
    title: string;
    value: string | number;
    unit?: string;
    icon: LucideIcon;
    trend?: string;
    status?: 'normal' | 'warning' | 'critical';
    subtext?: string;
}

export function StatusCard({ title, value, unit, icon: Icon, status = 'normal', subtext }: Props) {
    const isCritical = status === 'critical';
    const isWarning = status === 'warning';

    return (
        <Card className={cn(
            "group relative overflow-hidden transition-all duration-300 border",
            "hover:shadow-lg hover:-translate-y-1",
            isCritical ? "border-red-200 bg-red-50/50" : "border-slate-200 bg-white/80 backdrop-blur-sm"
        )}>
            {/* Background Gradient Blob */}
            <div className={cn(
                "absolute -right-6 -top-6 h-24 w-24 rounded-full opacity-0 blur-2xl transition-all group-hover:opacity-10",
                isCritical ? "bg-red-500" : "bg-blue-500"
            )} />

            <CardContent className="p-6 relative">
                <div className="flex justify-between items-start">
                    <div>
                        <p className="text-sm font-semibold text-slate-500 mb-1 uppercase tracking-wider">{title}</p>

                        <div className="flex items-baseline gap-1.5 my-1">
                            <h3 className={cn(
                                "text-3xl font-bold tracking-tight font-sans",
                                isCritical ? "text-red-700" : "text-slate-900"
                            )}>
                                {value}
                            </h3>
                            {unit && <span className="text-sm font-semibold text-slate-500">{unit}</span>}
                        </div>

                        {subtext && (
                            <Badge variant={isCritical ? "destructive" : "secondary"} className={cn(
                                "mt-2 font-medium",
                                !isCritical && "bg-slate-100 text-slate-600 hover:bg-slate-200"
                            )}>
                                {subtext}
                            </Badge>
                        )}
                    </div>

                    <div className={cn(
                        "flex h-12 w-12 items-center justify-center rounded-xl transition-colors border",
                        isCritical
                            ? "bg-red-100 border-red-200 text-red-600"
                            : "bg-blue-50 border-blue-100 text-blue-600 group-hover:bg-blue-100 group-hover:text-blue-700"
                    )}>
                        <Icon size={24} strokeWidth={2} />
                    </div>
                </div>

                {/* Status Indicator Bar */}
                <div className={cn(
                    "absolute bottom-0 left-0 h-1 w-full transition-all opacity-0 group-hover:opacity-100",
                    isCritical ? "bg-red-500" : "bg-blue-500"
                )} />
            </CardContent>
        </Card>
    );
}
